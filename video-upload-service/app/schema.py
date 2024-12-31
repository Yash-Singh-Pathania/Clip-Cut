from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class VideoStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    done = "done"

class Video(BaseModel):
    status: VideoStatus = Field(default=VideoStatus.uploaded)
    video_processing_status: str = ""
    audio_processing_status: str = ""
    upload_time: datetime
    processed_time: datetime = None
    total_processing_time: int = None
