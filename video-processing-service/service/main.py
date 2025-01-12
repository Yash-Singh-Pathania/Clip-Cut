import os
import json
import asyncio
import subprocess
import tempfile
from io import BytesIO
from typing import List, Tuple
from multiprocessing import Process

import redis
import requests
from bson import ObjectId
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from fastapi.responses import StreamingResponse

app = FastAPI()

# ------------------------------------------------------------------------------
# MongoDB / GridFS Setup
# ------------------------------------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)

# ------------------------------------------------------------------------------
# Redis Setup
# ------------------------------------------------------------------------------
redis_host = os.getenv("REDIS_HOST", "redis-service")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
redis_channel = redis.Redis(host=redis_host, port=redis_port)

# ------------------------------------------------------------------------------
# Monitoring Service URL (if you call it at start/end)
# ------------------------------------------------------------------------------
MONITORING_URL = os.getenv("MONITORING_URL", "http://monitoring-service.default.svc.cluster.local:80")


# ------------------------------------------------------------------------------
# Video Resolutions to Generate
# ------------------------------------------------------------------------------
resolutions = {
    "720p": (1280, 720),
    "480p": (640, 480),
    # Add more if needed, e.g. "360p": (480, 360),
}

# ------------------------------------------------------------------------------
# Helper: Download + Upload
# ------------------------------------------------------------------------------
async def get_video_bytes(video_id: str) -> bytes:
    """
    Download the original video from GridFS into memory as bytes.
    """
    buf = BytesIO()
    await grid_fs_bucket.download_to_stream(ObjectId(video_id), buf)
    return buf.getvalue()

async def upload_file_to_gridfs(file_name: str, contents: bytes) -> str:
    """
    Upload these bytes to Mongo GridFS, return the ID as str.
    """
    _id = await grid_fs_bucket.upload_from_stream(file_name, contents)
    return str(_id)

# ------------------------------------------------------------------------------
# Video Creation (FFmpeg)
# ------------------------------------------------------------------------------
def create_video(
    file_name: str,
    temp_path: str,
    resolution: str,
    dimensions: Tuple[int, int],
    subtitles_text: str | None,
    video_id: str,
):
    """
    Run ffmpeg to rescale. Then upload the result to GridFS, store the file ID in Redis 
    so the parent can retrieve it.
    """
    print(f"[create_video] Rescaling {file_name} to {resolution}")
    out_filename = f"{os.path.splitext(file_name)[0]}_{resolution}.mp4"
    width, height = dimensions

    ff_args = [
        "ffmpeg", "-y",
        "-i", temp_path,
        "-s", f"{width}x{height}",
        "-c:v", "libx264",
        "-c:a", "aac",
        out_filename
    ]
    ret = subprocess.call(ff_args)

    file_id = ""
    if ret == 0 and os.path.exists(out_filename):
        print(f"[create_video] Successfully created {out_filename}, uploading to GridFS...")
        with open(out_filename, "rb") as f:
            data = f.read()
        loop = asyncio.get_event_loop()
        file_id = loop.run_until_complete(upload_file_to_gridfs(out_filename, data))
        print(f"[create_video] Uploaded {out_filename} -> GridFS ID = {file_id}")
    else:
        print(f"[create_video] ffmpeg failed for resolution={resolution}")

    # Clean up local file
    try:
        os.remove(out_filename)
    except:
        pass

    # Store the resulting file_id in Redis for the parent process
    key = f"video_result_{video_id}_{resolution}"
    if file_id:
        redis_channel.set(key, file_id)
    else:
        redis_channel.set(key, "")

# ------------------------------------------------------------------------------
# The Main Video Processing Pipeline (runs in a child process)
# ------------------------------------------------------------------------------
def process_video(file_name: str, video_id: str):
    """
    Steps:
      1) (Optional) Let the monitoring service know we are starting.
      2) Download original video from GridFS.
      3) Ask audio service for transcription.
      4) Create a .txt file from that transcription (if any).
      5) Rescale video into multiple resolutions (sub-processes).
      6) Gather final file IDs from Redis.
      7) Publish final JSON to 'video_results'.
      8) (Optional) Let the monitoring service know we are done.
    """
    print(f"[process_video] Starting process for: {file_name} (video_id={video_id})")

    # 1) Notify monitoring service (start) - OPTIONAL
    try:
        start_url = f"{MONITORING_URL}/video-processing-start/{video_id}"
        resp_start = requests.post(start_url)
        if resp_start.status_code != 200:
            print(f"[process_video] Warning: Monitoring start call failed: {resp_start.text}")
        else:
            print("[process_video] Monitoring service notified: start")
    except Exception as e:
        print(f"[process_video] Could not notify monitoring service start: {e}")

    loop = asyncio.get_event_loop()

    # 2) Download from GridFS
    original_bytes = loop.run_until_complete(get_video_bytes(video_id))
    print(f"[process_video] Downloaded original video bytes from GridFS (ID={video_id}).")

    # 3) Call the audio service for transcription
    audio_url = os.getenv("AUDIO_SERVICE_URL", "http://audio-service.default.svc.cluster.local:83/audio")
    transcription_text = ""
    try:
        print(f"[process_video] Sending request to audio service -> {audio_url}")
        resp = requests.post(audio_url, params={"video_id": video_id}, timeout=600)
        if resp.status_code == 200:
            transcription_chunks = resp.json().get("transcription", [])
            transcription_text = " ".join([chunk["text"] for chunk in transcription_chunks])
            print(f"[process_video] Transcription received. Length: {len(transcription_text)} chars")
        else:
            print(f"[process_video] Audio service error: {resp.status_code}, no transcription.")
    except Exception as e:
        print(f"[process_video] Audio service request failed: {e}")

    # 4) Create a .txt file in GridFS if we have a transcription
    txt_file_id = ""
    if transcription_text.strip():
        txt_filename = f"{os.path.splitext(file_name)[0]}_transcription.txt"
        text_bytes = transcription_text.encode("utf-8")
        txt_file_id = loop.run_until_complete(upload_file_to_gridfs(txt_filename, text_bytes))
        print(f"[process_video] Transcription uploaded as file_id={txt_file_id}")
    else:
        print("[process_video] No transcription text, skipping .txt upload.")

    # 5) Rescale the original video in sub-processes
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(original_bytes)
        tmp_path = tmp.name
    print(f"[process_video] Created temp file: {tmp_path}")

    processes = []
    for res_label, dims in resolutions.items():
        proc = Process(
            target=create_video,
            args=(file_name, tmp_path, res_label, dims, None, video_id),
        )
        proc.start()
        processes.append(proc)

    # Wait for all sub-processes
    for proc in processes:
        proc.join()

    # Clean up
    try:
        os.remove(tmp_path)
    except:
        pass

    # 6) Gather new file IDs from Redis
    results_map = {}
    for res_label in resolutions.keys():
        redis_key = f"video_result_{video_id}_{res_label}"
        f_id = None
        for _ in range(50):  # poll up to 50 times
            val = redis_channel.get(redis_key)
            if val:
                f_id = val.decode("utf-8")
                redis_channel.delete(redis_key)
                break
            else:
                asyncio.run(asyncio.sleep(0.1))
        results_map[res_label] = f_id if f_id else ""

    # 7) Publish final message to 'video_results' channel
    #    (If the monitoring service also subscribes to this, it can pick it up.)
    final_message = {
        "event": "video_processed",
        "video_id": video_id,
        "file_name": file_name,
        "transcript_file_id": txt_file_id,
        "resolutions": results_map
    }
    redis_channel.publish("video_results", json.dumps(final_message))
    print(f"[process_video] Published final results to 'video_results' channel.")

    try:
        end_url = f"{MONITORING_URL}/video-processing-end/{video_id}"
        end_payload = {
            "processed_video_id": "",  # if you want to store a main mp4 ID here
            "transcription_id": txt_file_id,
            "video_processing_status": "done",
            "status": "done"
        }
        resp_end = requests.post(end_url, json=end_payload)
        if resp_end.status_code != 200:
            print(f"[process_video] Warning: Monitoring end call failed: {resp_end.text}")
        else:
            print("[process_video] Monitoring service notified: end")
    except Exception as e:
        print(f"[process_video] Monitoring service notifiedd: end ")

    print(f"[process_video] Done with video_id={video_id}.\n")

# ------------------------------------------------------------------------------
# Redis Pub/Sub Listener
# ------------------------------------------------------------------------------
def listen_for_videos():
    """
    Main loop:
      - Subscribes to 'video_uploads' for new videos
      - Possibly also handles 'video_results' internally if needed
    """
    pubsub = redis_channel.pubsub()
    pubsub.subscribe("video_uploads", "video_results")
    print("[listen_for_videos] Subscribed to Redis channels: 'video_uploads' & 'video_results'")

    loop = asyncio.get_event_loop()

    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        channel = message["channel"].decode("utf-8")
        if channel == "video_uploads":
            # e.g.: "myvideo.mp4,<gridfs_id>"
            data = message["data"].decode("utf-8").split(",")
            file_name, video_id = data[0], data[1]
            print(f"[listen_for_videos] Received upload event: {file_name}, {video_id}")
            Process(target=process_video, args=[file_name, video_id]).start()

        elif channel == "video_results":
            # If you want to do something internal on final results, you can handle it here.
            data_str = message["data"].decode("utf-8")
            try:
                data_json = json.loads(data_str)
                print(f"[listen_for_videos] Received final results for video_id={data_json.get('video_id')}")
            except:
                print("[listen_for_videos] Could not parse video_results as JSON:", data_str)

# ------------------------------------------------------------------------------
# Download Endpoint
# ------------------------------------------------------------------------------
@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Retrieve a file (video or text) from GridFS by _id and return it.
    """
    grid_out = await grid_fs_bucket.open_download_stream(ObjectId(file_id))
    return StreamingResponse(grid_out, media_type="application/octet-stream")

# ------------------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Typically you'd run:
      uvicorn main:app --host 0.0.0.0 --port 8000
    in one container, and also run listen_for_videos() 
    in the same or another container.

    For quick local testing, we just call listen_for_videos() so it blocks.
    """
    listen_for_videos()
