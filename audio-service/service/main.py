import asyncio
from io import BytesIO
import os
import subprocess
import tempfile

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import transformers
import torch

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
TASK = "automatic-speech-recognition"
MODEL = "./whisper-tiny"  # e.g., "openai/whisper-tiny.en"

# Since you said "I don't have GPU", we set device=-1 (CPU).
# We'll still pass torch_dtype=float16, but if it fails, we fallback to normal pipeline.
try:
    pipeline = transformers.pipeline(
        task=TASK,
        model=MODEL,
        tokenizer=MODEL,
        chunk_length_s=30,
        device=-1,  # CPU
        torch_dtype=torch.float16,  # half precision for speed, but might error if not supported
        generate_kwargs={"language": "en", "task": "transcribe"},  # force English
    )
except Exception:
    # Fallback: no half precision
    pipeline = transformers.pipeline(
        task=TASK,
        model=MODEL,
        tokenizer=MODEL,
        chunk_length_s=30,
        device=-1,  # CPU
        generate_kwargs={"language": "en", "task": "transcribe"},
    )


async def get_mongo_client():
    client = AsyncIOMotorClient(MONGO_URL)
    grid_fs_bucket = AsyncIOMotorGridFSBucket(client.video_status)
    return client, grid_fs_bucket


async def get_audio(video_id: str) -> BytesIO:
    """
    Download the video from GridFS into a BytesIO object.
    """
    _, grid_fs_bucket = await get_mongo_client()
    output_stream = BytesIO()
    await grid_fs_bucket.download_to_stream(ObjectId(video_id), output_stream)
    output_stream.seek(0)
    return output_stream


@app.post("/audio")
async def process_audio(video_id: str):
    """
    Extract audio from GridFS-stored MP4, force English transcription,
    and return JSON with timestamps.
    """
    # 1) Download video bytes from GridFS
    video_content = await get_audio(video_id)

    # 2) Save to temp .mp4
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
        temp_video.write(video_content.read())
        temp_video_path = temp_video.name

    # 3) Convert to .mp3 via ffmpeg
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name

    ffmpeg_returncode = subprocess.call(
        [
            "ffmpeg", "-y",
            "-i", temp_video_path,
            temp_audio_path,
        ]
    )
    if ffmpeg_returncode != 0:
        os.remove(temp_video_path)
        os.remove(temp_audio_path)
        raise HTTPException(
            status_code=500,
            detail="ffmpeg failed to extract audio. Possibly invalid/corrupted mp4.",
        )

    # 4) Run whisper pipeline (forced English)
    try:
        result = pipeline(temp_audio_path, return_timestamps=True)
        transcription = result["chunks"]  # "chunks" from the pipeline
    except Exception as e:
        os.remove(temp_video_path)
        os.remove(temp_audio_path)
        raise HTTPException(
            status_code=500, detail=f"ASR pipeline failed: {str(e)}"
        )

    # 5) Cleanup temp files
    os.remove(temp_audio_path)
    os.remove(temp_video_path)

    return {"transcription": transcription}
