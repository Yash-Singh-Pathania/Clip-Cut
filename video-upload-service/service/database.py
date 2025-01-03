import asyncio
import os
import logging
import httpx
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pymongo import ASCENDING, IndexModel

client = None
db = None
grid_fs_bucket = None
metadata_collection = None

async def init_mongo():
    """
    Initialize MongoDB connection, create the GridFS bucket,
    and set up indexes for metadata_collection.
    """
    global client, db, grid_fs_bucket, metadata_collection
    
    # 1. Initialize MongoDB Client
    mongo_url = os.getenv("MONGO_URL") or "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client.video_status
    
    # 2. GridFS Bucket
    grid_fs_bucket = AsyncIOMotorGridFSBucket(db)
    
    # 3. Metadata Collection
    metadata_collection = db.video_metadata

    # 4. Create Indexes
    indexes = [
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("type", ASCENDING)]),
    ]
    await metadata_collection.create_indexes(indexes)
    
    logging.info("MongoDB initialized, GridFS bucket created, indexes set.")


async def upload_video_to_db(filename, content, content_type, user_id):
    """
    Upload a video to GridFS, store metadata, and then attempt to
    notify the Monitoring Service in a try block. If notification fails,
    the function just logs the error and continues.
    """
    # 1. Upload video to GridFS
    video_id = await grid_fs_bucket.upload_from_stream(
        filename,
        content,
        metadata={"content_type": content_type, "type": "original"}
    )
    
    # 2. Insert document into metadata collection
    str_video_id = str(video_id)
    await metadata_collection.insert_one({
        "video_id": str_video_id,
        "filename": filename,
        "content_type": content_type,
        "user_id": user_id,
        "type": "original",
    })

    # 3. Attempt to notify the Monitoring Service in a try block
    try:
        async with httpx.AsyncClient() as client_http:
            # Example payload matching your VideoCreate schema
            payload = {
                "user_id": user_id,
                "raw_video_id": str_video_id,
                "processed_video_id": None,
                "transcription_id": None,
                "status": "created",
                "video_processing_status": "pending",
                "audio_processing_status": "pending",
                "video_processing_start": None,
                "video_processing_end": None,
                "audio_processing_start": None,
                "audio_processing_end": None,
                "upload_time": datetime.utcnow().isoformat(),
                "processed_time": None,
                "total_processing_time": None,
                "additonal_details": {
                    "filename": filename,
                    "content_type": content_type,
                },
            }

            # Adjust this URL if needed (e.g., 'http://monitoring-service/videos')
            monitoring_service_url = "http://monitoring-service/videos"

            response = await client_http.post(monitoring_service_url, json=payload)
            response.raise_for_status()
            logging.info("Successfully posted to monitoring-service for video_id=%s", str_video_id)

    except Exception:
        # If the call fails, log the exception and keep going
        logging.exception("Failed to send confirmation to monitoring service")

    return str_video_id


async def find_videos_by_user(user_id):
    """
    Query metadata collection to find videos by user_id.
    """
    results = await metadata_collection.find({"user_id": user_id}).to_list(length=100)
    return results

# If you'd like to test init_mongo() outside of FastAPI, you can do so:
if __name__ == "__main__":
    asyncio.run(init_mongo())
