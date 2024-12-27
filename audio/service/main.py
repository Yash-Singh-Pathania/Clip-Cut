import os
from typing import Dict, List

import aiofiles
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydub import AudioSegment
import requests
import transformers


class Timestamp(BaseModel):
    start: float
    end: float

class Transcription(BaseModel):
    timestamp: Timestamp
    text: str


TASK = 'automatic-speech-recognition'
MODEL = 'openai/whisper-base.en'


transcriptions: Dict[str, List[Transcription]] = {}
app = FastAPI()
try:
    pipeline = transformers.pipeline(TASK, MODEL, chunk_length_s=30, device=0)
except:
    pipeline = transformers.pipeline(TASK, MODEL, chunk_length_s=30)


async def stream_mp3(file_path: str):
    chunk_size = 1024
    async with aiofiles.open(file_path, mode='rb') as audio_file:
        while chunk := await audio_file.read(chunk_size):
            yield chunk


@app.get('/audio/audiofile/{video_id}', response_class=StreamingResponse, responses={
    200: {
        'content': {
            'audio/mpeg': {}
        },
        'description': 'MP3 audio file stream',
    },
})
async def get_audio(video_id: str):
    file_path = os.path.join('./audiofiles', video_id + '.mp3')
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail='No audio found with the provided video ID')

    headers = {
        'Content-Type': 'audio/mpeg',
        'Accept-Ranges': 'bytes'
    }

    return StreamingResponse(stream_mp3(file_path), headers=headers)


@app.get('/audio/transcription/{video_id}')
async def get_transcription(video_id: str) -> List[Transcription]:
    if video_id in transcriptions:
        return transcriptions[video_id]
    
    raise HTTPException(status_code=404, detail='id not found')


@app.post('/audio/')
async def process_audio(audiofile_url: str, video_id: str) -> str:
    response = requests.get(audiofile_url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Couldn't retrieve audio from provided url")

    if not os.path.isdir('./audiofiles'):
        os.mkdir('./audiofiles')

    temp_path = audiofile_url[audiofile_url.rfind('/') + 1:]
    audiofile_path = os.path.join('./audiofiles', video_id + '.mp3')

    try:
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(response.content)

        temp_audio = AudioSegment.from_file(temp_path)
        temp_audio.export(audiofile_path, format='mp3')
    except:
        raise HTTPException(status_code=500, detail='Failed to save temporary audio file')
    
    try:
        transcription = pipeline(audiofile_path, return_timestamps=True)['chunks']
    except:
        raise HTTPException(status_code=500, detail='Failed to perform transcription')
    
    transcriptions[video_id] = [
        Transcription(
            timestamp=Timestamp(start=t['timestamp'][0], end=t['timestamp'][1]),
            text=t['text'].strip()
        )
        for t in transcription
    ]

    os.remove(temp_path)    
    return video_id

