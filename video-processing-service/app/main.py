from fastapi import FastAPI
from pydantic import BaseModel
from app.worker import compress_video

app = FastAPI()


