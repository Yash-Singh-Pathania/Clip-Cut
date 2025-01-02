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


async def get_audio(video_id: str) -> bytes:
    output_stream = BytesIO()
    await grid_fs_bucket.download_to_stream(ObjectId(video_id), output_stream)
    with tempfile.NamedTemporaryFile("wb") as temp_video:
        temp_video.write(output_stream.getvalue())
        video_path = temp_video.name

        with tempfile.NamedTemporaryFile("wb", suffix=".mp3") as temp_audio:
            audio_path = temp_audio.name
            subprocess.call(
                ["ffmpeg", "-y", "-i", video_path, audio_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

            return temp_audio.read()


async def upload_file(file_name: str, contents) -> str:
    id = await grid_fs_bucket.upload_from_stream(file_name, contents)
    return str(id)


@app.post("/audio")
async def process_audio(video_id: str):
    audio_content = await get_audio(video_id)

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(audio_content)
        transcription = pipeline(temp_file.name, return_timestamps=True)["chunks"]
        return transcription
