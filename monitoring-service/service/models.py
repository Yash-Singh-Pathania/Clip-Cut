# models.py
from sqlalchemy import (
    Column, Integer, String, DateTime, JSON
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class VideoStatusDB(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)

    # GridFS IDs stored as strings
    raw_video_id = Column(String, nullable=True)
    processed_video_id = Column(String, nullable=True)
    transcription_id = Column(String, nullable=True)

    # Status fields
    status = Column(String, default="uploaded")
    video_processing_status = Column(String, default="inqueue")
    audio_processing_status = Column(String, default="not_started")

    # Timestamps
    video_processing_start = Column(DateTime, nullable=True)
    video_processing_end = Column(DateTime, nullable=True)
    audio_processing_start = Column(DateTime, nullable=True)
    audio_processing_end = Column(DateTime, nullable=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    processed_time = Column(DateTime, nullable=True)

    # Additional fields
    total_processing_time = Column(Integer, nullable=True)

    # Arbitrary metadata
    # If your Postgres version supports JSONB, prefer JSONB over JSON
    metadata = Column(JSONB, nullable=True)
