import asyncio
from io import BytesIO
import json
from multiprocessing import Process
import os
import subprocess
import tempfile

# from typing import List

# import aiofiles
from bson import ObjectId

# from fastapi import FastAPI, HTTPException
# from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

# from pydantic import BaseModel
import redis
import transformers

db_client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = db_client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)
redis_channel = redis.Redis(host="redis-service", port=6379)

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

"""
class TranscriptionModel(BaseModel):
    timestamp: List[float]
    text: str

app = FastAPI()

if not os.path.isdir("./localstorage"):
    os.mkdir("./localstorage")


async def stream_mp3(file_path: str):
    chunk_size = 1024
    async with aiofiles.open(file_path, mode="rb") as audio_file:
        while chunk := await audio_file.read(chunk_size):
            yield chunk


@app.get(
    "/audio/audio/{user_id}/{video_id}/{lang}",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "MP3 audio file stream",
        },
    },
)
async def get_audio(user_id: str, video_id: str, lang: str):
    file_path = os.path.join(
        "./localstorage", user_id, video_id, "audio", lang + ".mp3"
    )
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="No audio found for the given video with the given language",
        )

    headers = {"Content-Type": "audio/mpeg", "Accept-Ranges": "bytes"}

    return StreamingResponse(stream_mp3(file_path), headers=headers)


@app.get("/audio/transcription/{user_id}/{video_id}/{lang}")
async def get_transcription(
    user_id: str, video_id: str, lang: str
) -> List[TranscriptionModel]:
    transcription_path = os.path.join(
        "./localstorage", user_id, video_id, "transcription", lang + ".json"
    )
    if not os.path.isfile(transcription_path):
        raise HTTPException(
            status_code=404,
            detail="Transcription not found for given video with given language",
        )

    with open(transcription_path, "r") as f:
        transcription_json = f.read()

    return json.loads(transcription_json)
"""


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


def process_audio(file_name: str, video_id: str):
    loop = asyncio.get_event_loop()
    audio_content = loop.run_until_complete(get_audio(video_id))
    loop.run_until_complete(file_name + ".mp3", audio_content)
    print(f"Uploaded audio {file_name}.mp3 to DB")

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(audio_content)
        transcription = pipeline(temp_file.name, return_timestamps=True)["chunks"]
        transcription_json = json.dumps(transcription)
        loop.run_until_complete(file_name + ".json", transcription_json)
        print(f"Uploaded transcription {file_name}.json to DB")


def listen_for_uploads():
    pubsub = redis_channel.pubsub()
    pubsub.subscribe("video_uploads")
    print("Subscribed to video_uploads Redis channel")

    for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"].decode("utf-8").split(",")
            file_name, video_id = data[0], data[1]
            print(f"Got {file_name},{video_id} from channel, processing")
            Process(target=process_audio, args=[file_name, video_id]).start()
