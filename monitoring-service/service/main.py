# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from .database import engine, SessionLocal
from .models import Base, VideoStatusDB
from .schema import VideoCreate, VideoUpdate, VideoRead, VideoStatusEnum

app = FastAPI(title="Monitoring Service with Postgres + GridFS IDs")

# Create table if not exists (quick start)
Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency that provides a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/videos", response_model=VideoRead)
def create_video(video_data: VideoCreate, db: Session = Depends(get_db)):
    """
    Create a new video record in Postgres, storing references
    to GridFS (Mongo) if provided.
    """
    db_video = VideoStatusDB(
        user_id=video_data.user_id,
        raw_video_id=video_data.raw_video_id,
        processed_video_id=video_data.processed_video_id,
        transcription_id=video_data.transcription_id,
        status=video_data.status,
        video_processing_status=video_data.video_processing_status,
        audio_processing_status=video_data.audio_processing_status,
        video_processing_start=video_data.video_processing_start,
        video_processing_end=video_data.video_processing_end,
        audio_processing_start=video_data.audio_processing_start,
        audio_processing_end=video_data.audio_processing_end,
        upload_time=video_data.upload_time or datetime.utcnow(),
        processed_time=video_data.processed_time,
        total_processing_time=video_data.total_processing_time,
        additonal_details=video_data.additonal_details,
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)

    return db_video

@app.get("/videos/{video_id}", response_model=VideoRead)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a video record by ID.
    """
    db_video = db.query(VideoStatusDB).filter(VideoStatusDB.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@app.get("/videos", response_model=list[VideoRead])
def list_videos_by_user(user_id: str, db: Session = Depends(get_db)):
    """
    List all videos for a given user.
    """
    videos = db.query(VideoStatusDB).filter(VideoStatusDB.user_id == user_id).all()
    return videos

@app.patch("/videos/{video_id}", response_model=VideoRead)
def update_video(video_id: int, updates: VideoUpdate, db: Session = Depends(get_db)):
    """
    Partially update a video record. 
    If an update sets status=done, auto-set processed_time and total_processing_time.
    Merge additonal_details if needed, or overwrite.
    """
    db_video = db.query(VideoStatusDB).filter(VideoStatusDB.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")

    data = updates.dict(exclude_unset=True)

    # Handle additonal_details separately if you want to merge
    new_additonal_details = data.pop("additonal_details", None)
    if new_additonal_details is not None:
        if db_video.additonal_details is None:
            db_video.additonal_details = {}
        # Merge or overwrite keys
        for k, v in new_additonal_details.items():
            db_video.additonal_details[k] = v

    # If status is changed to 'done', compute processed_time
    if "status" in data and data["status"] == VideoStatusEnum.done:
        db_video.processed_time = datetime.utcnow()
        if db_video.upload_time:
            delta = db_video.processed_time - db_video.upload_time
            db_video.total_processing_time = int(delta.total_seconds())

    # Apply remaining updates directly
    for key, value in data.items():
        setattr(db_video, key, value)

    db.commit()
    db.refresh(db_video)
    return db_video
## vido -postgres 
## the converted video id  processed_video : 
### the thumbnail : ( thumbnail image )