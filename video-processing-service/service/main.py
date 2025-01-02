import asyncio
from bson import ObjectId
import cv2
from io import BytesIO
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from multiprocessing import Process
import redis
import tempfile
import os


db_client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = db_client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)

redis_channel = redis.Redis(host="redis-service", port=6379)

resolutions = {
    "1080P": (1920, 1080),
    "720P": (1280, 720),
    "480P": (640, 480),
    "360P": (480, 360),
    "240P": (320, 240),
}


async def get_video(video_id: str, output_stream: BytesIO):
    await grid_fs_bucket.download_to_stream(ObjectId(video_id), output_stream)


async def upload_video(file_name: str, contents) -> str:
    id = await grid_fs_bucket.upload_from_stream(file_name, contents)
    return str(id)


def process_video(file_name: str, video_id: str):
    output_stream = BytesIO()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_video(video_id, output_stream))
    print(f"Downloaded {video_id} from DB")

    with tempfile.NamedTemporaryFile("wb") as temp_video:
        temp_video.write(output_stream.getvalue())
        temp_path = temp_video.name

        for resolution, dimensions in resolutions.values():
            print(f"Rescaling {file_name} to {dimensions}")

            cap = cv2.VideoCapture(temp_path)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")

            with tempfile.NamedTemporaryFile("wb") as rescaled:
                out = cv2.VideoWriter(
                    rescaled.name, fourcc, int(cap.get(cv2.CAP_PROP_FPS)), dimensions
                )

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    resized_frame = cv2.resize(frame, dimensions)
                    out.write(resized_frame)

                tagged_filename = f"{file_name}_{resolution}.mp4"
                video_id = loop.run_until_complete(upload_video(tagged_filename, rescaled.read()))
                print(f"Uploaded {tagged_filename} to DB")
                redis_channel.publish("rescaled_videos", f"{tagged_filename},{video_id}")
                out.release()

            cap.release()


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
