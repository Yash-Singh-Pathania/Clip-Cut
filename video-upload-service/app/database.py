from motor.motor_asyncio import AsyncIOMotorClient
from gridfs import GridFSBucket
import os

client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client.video_status
grid_fs_bucket = GridFSBucket(db)
