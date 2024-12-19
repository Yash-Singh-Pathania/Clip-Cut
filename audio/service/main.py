from fastapi import FastAPI, HTTPException
import os
from pydantic import BaseModel
import requests
import transformers
from typing import Dict, List

TASK = 'automatic-speech-recognition'
MODEL = 'openai/whisper-base.en'

app = FastAPI()

class Timestamp(BaseModel):
    start: float
    end: float

class Transcription(BaseModel):
    timestamp: Timestamp
    text: str

pipeline = transformers.pipeline(TASK, MODEL, chunk_length_s=30, device=1)
transcriptions: Dict[str, List[Transcription]] = {}

@app.get('/transcriptions/{transcription_id}')
async def get_transcription(transcription_id: str) -> List[Transcription]:
    if transcription_id in transcriptions:
        return transcriptions[transcription_id]
    
    raise HTTPException(status_code=404, detail='id not found')

@app.post('/transcriptions/')
async def create_transcription(audiofile_url: str) -> str:
    response = requests.get(audiofile_url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Couldn't retrieve audio from provided url")

    audiofile_path = audiofile_url[audiofile_url.rfind('/') + 1:]

    try:
        with open(audiofile_path, 'wb') as audiofile:
            audiofile.write(response.content)
    except:
        raise HTTPException(status_code=500, detail='Failed to save temporary audio file')
    
    try:
        transcription = pipeline(audiofile_path, return_timestamps=True)['chunks']
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to perform transcription: ' + e)

    transcription_id = str(len(transcriptions))
    transcriptions[transcription_id] = [
        Transcription(
            timestamp=Timestamp(start=t['timestamp'][0], end=t['timestamp'][1]),
            text=t['text']
        )
        for t in transcription
    ]

    os.remove(audiofile_path)
    return transcription_id
