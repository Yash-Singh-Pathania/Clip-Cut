# schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class VideoStatusEnum(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    done = "done"

class VideoUpdate(BaseModel):
    processed_video_id: Optional[str] = None
    transcription_id: Optional[str] = None

    status: Optional[VideoStatusEnum] = None
    video_processing_status: Optional[str] = None
    audio_processing_status: Optional[str] = None

    video_processing_end: Optional[datetime] = None
    total_processing_time: Optional[int] = None

    # Add more if needed

    class Config:
        orm_mode = True
