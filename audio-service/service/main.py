import asyncio
from io import BytesIO
import json
import os
import subprocess
import tempfile

from bson import ObjectId
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import transformers

app = FastAPI()
db_client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = db_client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)

TASK = "automatic-speech-recognition"
MODEL = "./whisper-tiny"


try:
    pipeline = transformers.pipeline(
        task=TASK, model=MODEL, tokenizer=MODEL, chunk_length_s=30, device=0
    )
except:
    pipeline = transformers.pipeline(
        task=TASK, model=MODEL, tokenizer=MODEL, chunk_length_s=30
    )


async def get_audio(video_id: str) -> BytesIO:
    output_stream = BytesIO()
    grid_fs_bucket.download_to_stream(ObjectId(video_id), output_stream)
    return output_stream


@app.post("/audio")
def process_audio(video_id: str):
    video_content = asyncio.run(get_audio(video_id))
    video_path = f"./{video_id}.mp4"
    with open(video_path, "wb") as video:
        video.write(video_content.read())

    audio_path = f"./{video_id}.mp3"
    subprocess.call(
        ["ffmpeg", "-y", "-i", video_path, audio_path],
    )

    transcription = pipeline(audio_path, return_timestamps=True)["chunks"]
    response = {"transcription": transcription}

    os.remove(audio_path)
    os.remove(video_path)

    return response
