# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class VideoStatusEnum(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    done = "done"

class VideoCreate(BaseModel):
    user_id: str
    raw_video_id: Optional[str] = None
    processed_video_id: Optional[str] = None
    transcription_id: Optional[str] = None

    status: VideoStatusEnum = Field(default=VideoStatusEnum.uploaded)
    video_processing_status: str = Field(default="inqueue")
    audio_processing_status: str = Field(default="not_started")

    video_processing_start: Optional[datetime] = None
    video_processing_end: Optional[datetime] = None
    audio_processing_start: Optional[datetime] = None
    audio_processing_end: Optional[datetime] = None
    upload_time: Optional[datetime] = None
    processed_time: Optional[datetime] = None
    total_processing_time: Optional[int] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)

class VideoUpdate(BaseModel):
    user_id: Optional[str] = None
    raw_video_id: Optional[str] = None
    processed_video_id: Optional[str] = None
    transcription_id: Optional[str] = None

    status: Optional[VideoStatusEnum] = None
    video_processing_status: Optional[str] = None
    audio_processing_status: Optional[str] = None

    video_processing_start: Optional[datetime] = None
    video_processing_end: Optional[datetime] = None
    audio_processing_start: Optional[datetime] = None
    audio_processing_end: Optional[datetime] = None
    processed_time: Optional[datetime] = None
    total_processing_time: Optional[int] = None

    metadata: Optional[Dict[str, Any]] = None

class VideoRead(BaseModel):
    """
    Used for returning data to the client.
    """
    id: int
    user_id: str

    raw_video_id: Optional[str]
    processed_video_id: Optional[str]
    transcription_id: Optional[str]

    status: VideoStatusEnum
    video_processing_status: str
    audio_processing_status: str

    video_processing_start: Optional[datetime]
    video_processing_end: Optional[datetime]
    audio_processing_start: Optional[datetime]
    audio_processing_end: Optional[datetime]
    upload_time: Optional[datetime]
    processed_time: Optional[datetime]
    total_processing_time: Optional[int]

    metadata: Dict[str, Any]

    class Config:
        orm_mode = True
