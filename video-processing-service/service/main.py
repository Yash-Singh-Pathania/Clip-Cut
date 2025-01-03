import asyncio
from bson import ObjectId
import cv2
from io import BytesIO
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from multiprocessing import Process
import redis
import requests
import subprocess
import tempfile
from typing import List, Tuple
import os


db_client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = db_client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)

redis_channel = redis.Redis(host="redis-service", port=6379)

resolutions = {
    "720P": (1280, 720),
    "480P": (640, 480),
    "360P": (480, 360),
}


def create_video(
    original_name: str, original_path: str, resolution: Tuple[int, int], subtitles: str
):
    cap = cv2.VideoCapture(original_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as subtitle_file:
        subtitle_file.write(subtitles)
        subtitle_path = subtitle_file.name

    with tempfile.NamedTemporaryFile("wb") as rescaled:
        out = cv2.VideoWriter(
            rescaled.name, fourcc, int(cap.get(cv2.CAP_PROP_FPS)), resolution
        )

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            resized_frame = cv2.resize(frame, resolution)
            out.write(resized_frame)

        out.release()

        # fmt: off
        ffmpeg_process = subprocess.Popen(
            [
                "ffmpeg",
                "-y", # overwrite automatically
                "-i", rescaled.name, # input 1 (video) from stdin        
                "-vf", f"subtitles={subtitle_path}", # add subtitles            
                "-c:v", "libx264", # copy video codec            
                "-c:a", "aac", # encode audio to AAC            
                "-f", "mp4", # output an mp4            
                rescaled.name, # output to tempfile we made
            ],
            stdout=subprocess.PIPE,
            pass_fds=(3,),
        )
        # fmt: on
        ffmpeg_process.wait()

        tagged_filename = f"{original_name}{resolution}.mp4"
        loop = asyncio.get_event_loop()
        loop.run_until_complete(upload_video(tagged_filename, rescaled.read()))
        print(f"Uploaded {tagged_filename} to DB")

    cap.release()


def get_transcription(transcription_json) -> str:
    srt_lines = []
    for idx, entry in enumerate(transcription_json, start=1):
        start: float = entry["timestamp"][0]
        end: float = entry["timestamp"][1]
        text: str = entry["text"]

        def to_srt_time(seconds: float) -> str:
            milliseconds = int((seconds - int(seconds)) * 1000)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

        srt_lines.append(
            f"{idx}\n{to_srt_time(start)} --> {to_srt_time(end)}\n{text}\n"
        )

    return "\n".join(srt_lines)


async def get_video(video_id: str, output_stream: BytesIO):
    await grid_fs_bucket.download_to_stream(ObjectId(video_id), output_stream)


async def upload_video(file_name: str, contents) -> str:
    id = await grid_fs_bucket.upload_from_stream(file_name, contents)
    return str(id)


def process_video(file_name: str, video_id: str):
    loop = asyncio.get_event_loop()

    output_stream = BytesIO()
    loop.run_until_complete(get_video(video_id, output_stream))
    print(f"Downloaded {video_id} from DB")

    transcription = requests.post(
        "http://audio-service.default.svc.cluster.local:83/audio",
        params={"video_id": video_id},
    ).json()["transcription"]
    subtitles = get_transcription(transcription)
    print(f"Got transcription for {video_id}")

    with tempfile.NamedTemporaryFile("wb") as temp_video:
        temp_video.write(output_stream.getvalue())
        temp_path = temp_video.name
        processes: List[Process] = []

        for resolution, dimensions in resolutions.values():
            print(f"Rescaling {file_name} to {dimensions}")
            process = Process(
                target=create_video, args=[file_name, temp_path, resolution, subtitles]
            )
            process.start()
            processes.append(process)

        for process in processes:
            process.join()


def listen_for_videos():
    pubsub = redis_channel.pubsub()
    pubsub.subscribe("video_uploads")
    print(f"Subscribed to Redis channel: video_uploads")

    for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"].decode("utf-8").split(",")
            file_name, video_id = data[0], data[1]
            print(f"Got {file_name},{video_id} from channel, processing")
            Process(target=process_video, args=[file_name, video_id]).start()


if __name__ == "__main__":
    listen_for_videos()
