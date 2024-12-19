from fastapi import FastAPI, HTTPException
import requests
import transformers
from typing import Dict

TASK = 'automatic-speech-recognition'
MODEL = 'openai/whisper-base.en'

app = FastAPI()
pipeline = transformers.pipeline(TASK, MODEL, device=1)
transcriptions: Dict[str, str] = {}

@app.get('/transcriptions/{transcription_id}')
async def get_transcription(transcription_id: str):
    if transcription_id in transcriptions:
        return {'transcription': transcriptions[transcription_id]}
    
    raise HTTPException(status_code=404, detail='id not found')

@app.post('/transcriptions/')
async def create_transcription(audiofile_url: str):
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
        transcription = pipeline(audiofile_path)['text']
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to perform transcription: ' + e)

    transcription_id = str(len(transcriptions))
    transcriptions[transcription_id] = transcription
    return transcription_id