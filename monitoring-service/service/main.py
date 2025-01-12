# main.py (monitoring_service)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
from typing import Dict, Optional

import os
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from .database import engine, SessionLocal
from .models import Base, VideoStatusDB
from .schema import VideoStatusEnum, VideoUpdate

app = FastAPI(title="Monitoring Service with Embedded Download Links")

# ------------------------------------------------------------------------------
# Postgres Setup
# ------------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency that provides a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------------------------------------------
# Mongo / GridFS Setup
# ------------------------------------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
mongo_client = AsyncIOMotorClient(MONGO_URL)
mongo_db = mongo_client.video_status  # same DB the video processing uses
grid_fs_bucket = AsyncIOMotorGridFSBucket(mongo_db)

# ------------------------------------------------------------------------------
# WebSocket Tracking
# ------------------------------------------------------------------------------
connected_clients = []

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint. The frontend connects here to receive real-time
    updates when a video is fully processed.
    """
    await websocket.accept()
    connected_clients.append(websocket)
    print("[Monitoring] WebSocket client connected.")
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        print("[Monitoring] WebSocket client disconnected.")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast(message: dict):
    """
    Broadcast a JSON-serializable dictionary to all connected WebSocket clients.
    """
    to_remove = []
    for ws in connected_clients:
        try:
            await ws.send_json(message)
        except:
            to_remove.append(ws)
    for ws in to_remove:
        if ws in connected_clients:
            connected_clients.remove(ws)

# ------------------------------------------------------------------------------
# Helper: Parse Username from raw_video_id
# ------------------------------------------------------------------------------
def parse_username_from_videoid(raw_video_id: str) -> str:
    """
    If your raw_video_id looks like 'username_something', we parse 'username'
    as the user name. If there's no underscore, we default to 'unknown'.
    """
    parts = raw_video_id.split("_", 1)
    if parts:
        return parts[0]
    return "unknown"

# ------------------------------------------------------------------------------
# Download Endpoint (streams from GridFS)
# ------------------------------------------------------------------------------
@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Retrieve a file (video or text) from GridFS by _id and return it.
    """
    try:
        object_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file_id (not a valid ObjectId)")

    grid_out = await grid_fs_bucket.open_download_stream(object_id)
    if not grid_out:
        raise HTTPException(status_code=404, detail="File not found in GridFS")

    return StreamingResponse(grid_out, media_type="application/octet-stream")

# ------------------------------------------------------------------------------
# video-processing-start
# ------------------------------------------------------------------------------
@app.post("/video-processing-start/{video_id}")
def video_processing_start(video_id: str, db: Session = Depends(get_db)):
    """
    Called when video processing starts. We'll either find an existing record
    or create a new one if none exists for raw_video_id = video_id.
    Also parse the username from 'video_id' if you store the pattern 'username_something'.
    """
    # Try to find existing row
    db_video = db.query(VideoStatusDB).filter(VideoStatusDB.raw_video_id == video_id).first()

    if not db_video:
        # Create a new record
        user_id = parse_username_from_videoid(video_id)
        db_video = VideoStatusDB(
            user_id=user_id,
            raw_video_id=video_id,
            status="uploaded",
            video_processing_status="processing",
            video_processing_start=datetime.utcnow(),
            upload_time=datetime.utcnow(),
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return {
            "message": f"Created record & marked processing start for raw_video_id={video_id}",
            "video_id": video_id
        }

    # Else, update existing
    db_video.video_processing_status = "processing"
    db_video.video_processing_start = datetime.utcnow()
    db.commit()
    db.refresh(db_video)

    return {
        "message": f"Video processing started (existing record updated) for raw_video_id={video_id}",
        "video_id": video_id
    }

# ------------------------------------------------------------------------------
# video-processing-end
# ------------------------------------------------------------------------------
@app.post("/video-processing-end/{video_id}")
async def video_processing_end(
    video_id: str,
    updates: VideoUpdate,
    db: Session = Depends(get_db)
):
    """
    Called when the video is fully processed.
    We expect the JSON to include something like:
      {
        "processed_video_id": "...",
        "transcription_id": "...",
        "resolutions": { "720p": "<fileID720>", "480p": "<fileID480>" },
        "status": "done"
      }

    We'll set status=done, compute total time, then broadcast 
    a 'video_processed' event with embedded /download/{file_id} links (from *this* service).
    """
    db_video = db.query(VideoStatusDB).filter(VideoStatusDB.raw_video_id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=404,
            detail=f"No matching video record with raw_video_id={video_id}"
        )

    # Mark the status as done
    db_video.status = "done"
    db_video.video_processing_status = "done"
    db_video.video_processing_end = datetime.utcnow()

    # If we have a start time and an upload time, compute total
    if db_video.upload_time and db_video.video_processing_end:
        delta = db_video.video_processing_end - db_video.upload_time
        db_video.total_processing_time = int(delta.total_seconds())

    # Update fields from the VideoUpdate model
    data = updates.dict(exclude_unset=True)
    if "processed_video_id" in data:
        db_video.processed_video_id = data["processed_video_id"]
    if "transcription_id" in data:
        db_video.transcription_id = data["transcription_id"]

    db.commit()
    db.refresh(db_video)

    MONITORING_DOWNLOAD_BASE = "http://localhost:8002/download"

    # If you included "resolutions" in the request body, e.g. data["resolutions"]
    resolutions_dict = data.get("resolutions", {})
    # Build "download_links" from resolution IDs
    download_links = {}
    for res_label, fid in resolutions_dict.items():
        download_links[res_label] = f"{MONITORING_DOWNLOAD_BASE}/{fid}"

    # Build link for transcript
    transcript_id = data.get("transcription_id", "")
    download_transcript = None
    if transcript_id:
        download_transcript = f"{MONITORING_DOWNLOAD_BASE}/{transcript_id}"

    # Broadcast message
    msg = {
        "event": "video_processed",
        "video_id": video_id,
        "file_name": db_video.raw_video_id,  # or something else
        "transcript_file_id": db_video.transcription_id,
        "resolutions": resolutions_dict,  # raw IDs
        "download_links": download_links,
        "download_transcript": download_transcript,
        "message": "Video fully processed. Ready to download."
    }
    await broadcast(msg)

    return {
        "message": "Video processing ended",
        "video_id": video_id,
        "status": "done"
    }
