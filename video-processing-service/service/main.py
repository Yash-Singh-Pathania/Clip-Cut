import asyncio
from bson import ObjectId
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
    "720p": (1280, 720),
    "480p": (640, 480),
    "360p": (480, 360),
}


def create_video(
    original_name: str,
    original_path: str,
    resolution: str,
    dimensions: Tuple[int, int],
    subtitles: str | None,
):
    tagged_filename = f"{os.path.splitext(original_name)[0]}_{resolution}.mp4"
    print(f"Creating {tagged_filename}")

    if subtitles is not None:
        with tempfile.NamedTemporaryFile(suffix=".srt") as subtitles_file:
            subtitles_file.write(subtitles.encode("utf-8"))
            # fmt: off
            ffmpeg_retcode = subprocess.call(
                [
                    "ffmpeg",
                    "-y",
                    "-i", original_path,
                    "-vf", f"subtitles={subtitles_file.name}",
                    "-s", f"{dimensions[0]}x{dimensions[1]}",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    tagged_filename
                ]
            )

            if ffmpeg_retcode != 0:
                print("Retrying without subtitles")
                ffmpeg_retcode = subprocess.call(
                    [
                        "ffmpeg",
                        "-y",
                        "-i", original_path,
                        "-s", f"{dimensions[0]}x{dimensions[1]}",
                        "-c:v", "libx264",
                        "-c:a", "aac",
                        tagged_filename
                    ]
                )
            # fmt: on
    else:
        # fmt: off
        ffmpeg_retcode = subprocess.call(
            [
                "ffmpeg",
                "-y",
                "-i", original_path,
                "-s", f"{dimensions[0]}x{dimensions[1]}",
                "-c:v", "libx264",
                "-c:a", "aac",
                tagged_filename
            ]
        )
        # fmt: on

    if ffmpeg_retcode == 0:
        with open(tagged_filename, "rb") as rescaled:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(upload_video(tagged_filename, rescaled.read()))
            print(f"Uploaded {tagged_filename} to DB")
    else:
        print(f"Error rescaling {original_name} to {dimensions}")


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
    print(f"Downloaded {file_name} from DB")

    transcription_response = requests.post(
        "http://audio-service.default.svc.cluster.local:83/audio",
        params={"video_id": video_id},
    )

    if transcription_response.status_code == 200:        
        subtitles = get_transcription(transcription_response.json()["transcription"])
        print(f"Got subtitles for {file_name}")
    else:
        subtitles = None
        print(f"No subtitles available for {file_name}")

    with tempfile.NamedTemporaryFile("w+b", suffix=".mp4") as temp_video:
        temp_video.write(output_stream.getvalue())
        temp_path = temp_video.name
        processes: List[Process] = []

        for resolution, dimensions in resolutions.items():
            print(f"Rescaling {file_name} to {resolution}p")
            process = Process(
                target=create_video,
                args=[
                    file_name,
                    temp_path,
                    resolution,
                    dimensions,
                    subtitles,
                ],
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
