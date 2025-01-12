# models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class VideoStatusDB(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)

    raw_video_id = Column(String, nullable=True)
    processed_video_id = Column(String, nullable=True)
    transcription_id = Column(String, nullable=True)

    status = Column(String, default="uploaded")
    video_processing_status = Column(String, default="inqueue")
    audio_processing_status = Column(String, default="not_started")

    video_processing_start = Column(DateTime, nullable=True)
    video_processing_end = Column(DateTime, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    total_processing_time = Column(Integer, nullable=True)
