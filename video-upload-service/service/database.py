import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pymongo import ASCENDING, IndexModel

client = None
db = None
grid_fs_bucket = None
metadata_collection = None

async def init_mongo():
    global client, db, grid_fs_bucket, metadata_collection
    
    # 1. Initialize MongoDB Client
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
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

async def upload_video_to_db(filename, content, content_type, user_id):
    # Upload video to GridFS
    video_id = await grid_fs_bucket.upload_from_stream(
        filename, 
        content, 
        metadata={"content_type": content_type, "type": "original"}
    )
    
    # Insert document into metadata collection
    await metadata_collection.insert_one({
        "video_id": str(video_id),
        "filename": filename,
        "content_type": content_type,
        "user_id": user_id,
        "type": "original",
    })
    return str(video_id)

async def find_videos_by_user(user_id):
    # Query metadata collection to find videos by user_id
    results = await metadata_collection.find({"user_id": user_id}).to_list(length=100)
    return results

if __name__ == "__main__":
    asyncio.run(init_mongo())
    # After init, you can call upload_video_to_db(...) or find_videos_by_user(...) in other async contexts.
