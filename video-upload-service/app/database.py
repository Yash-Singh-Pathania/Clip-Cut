from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import os

client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)