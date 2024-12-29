import json
import os
from typing import List

import aiofiles
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydub import AudioSegment
import requests
import transformers


class TranscriptionModel(BaseModel):
    timestamp: List[float]
    text: str


TASK = "automatic-speech-recognition"
MODEL = "openai/whisper-base.en"


app = FastAPI()
try:
    pipeline = transformers.pipeline(TASK, MODEL, chunk_length_s=30, device=0)
except:
    pipeline = transformers.pipeline(TASK, MODEL, chunk_length_s=30)


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


@app.post("/audio/")
async def process_audio(audiofile_url: str, user_id: str, video_id: str) -> str:
    response = requests.get(audiofile_url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Couldn't retrieve audio from provided url"
        )

    user_folder = os.path.join("./localstorage", user_id)
    video_folder = os.path.join(user_folder, video_id)
    audio_folder = os.path.join(video_folder, "audio")
    transcription_folder = os.path.join(video_folder, "transcription")

    if not os.path.isdir(audio_folder):
        os.makedirs(audio_folder)

    if not os.path.isdir(transcription_folder):
        os.makedirs(transcription_folder)

    temp_path = audiofile_url[audiofile_url.rfind("/") + 1 :]
    audiofile_path = os.path.join(audio_folder, "en.mp3")
    transcription_path = os.path.join(transcription_folder, "en.json")

    with open(temp_path, "wb") as temp_file:
        temp_file.write(response.content)

    temp_audio = AudioSegment.from_file(temp_path)
    temp_audio.export(audiofile_path, format="mp3")

    transcription = pipeline(audiofile_path, return_timestamps=True)["chunks"]
    with open(transcription_path, "w") as f:
        f.write(json.dumps(transcription))
    os.remove(temp_path)
    return video_id
