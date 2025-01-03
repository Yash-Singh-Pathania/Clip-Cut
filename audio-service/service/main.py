import asyncio
from io import BytesIO
import os
import subprocess
import tempfile

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import transformers

app = FastAPI()

# Make sure your MONGO_URL is set in the environment or .env
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)

TASK = "automatic-speech-recognition"
MODEL = "./whisper-tiny"

try:
    pipeline = transformers.pipeline(
        task=TASK, 
        model=MODEL, 
        tokenizer=MODEL, 
        chunk_length_s=30, 
        device=0
    )
except Exception:
    pipeline = transformers.pipeline(
        task=TASK, 
        model=MODEL, 
        tokenizer=MODEL, 
        chunk_length_s=30
    )

async def get_audio(video_id: str) -> BytesIO:
    """Download the video from GridFS into a BytesIO object."""
    output_stream = BytesIO()
    # IMPORTANT: Always await your async GridFS calls
    await grid_fs_bucket.download_to_stream(ObjectId(video_id), output_stream)
    output_stream.seek(0)
    return output_stream

@app.post("/audio")
async def process_audio(video_id: str):
    """Extract audio from a GridFS-stored MP4 video and run ASR (whisper)."""
    # 1) Download video bytes
    video_content = await get_audio(video_id)

    # 2) Save to a temp .mp4
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
        temp_video.write(video_content.read())
        temp_video_path = temp_video.name

    # 3) Convert to MP3 using ffmpeg
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name

    ffmpeg_returncode = subprocess.call([
        "ffmpeg",
        "-y",             # overwrite
        "-i", temp_video_path,
        temp_audio_path,
    ])
    if ffmpeg_returncode != 0:
        # If ffmpeg failed, remove temp files and raise an error
        os.remove(temp_video_path)
        os.remove(temp_audio_path)
        raise HTTPException(
            status_code=500, 
            detail="ffmpeg failed to extract audio. Possibly invalid/corrupted mp4."
        )

    # 4) Run the pipeline on the extracted .mp3
    try:
        result = pipeline(temp_audio_path, return_timestamps=True)
        transcription = result["chunks"]  # "chunks" from the whisper pipeline
    except Exception as e:
        os.remove(temp_video_path)
        os.remove(temp_audio_path)
        raise HTTPException(
            status_code=500, 
            detail=f"ASR pipeline failed: {str(e)}"
        )

    # 5) Clean up temp files
    os.remove(temp_audio_path)
    os.remove(temp_video_path)

    return {"transcription": transcription}