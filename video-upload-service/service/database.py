from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import os

client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client.video_status
grid_fs_bucket = AsyncIOMotorGridFSBucket(db)


async def upload_video_to_db(filename, content, content_type):
    video_id = await grid_fs_bucket.upload_from_stream(
        filename, content, metadata={"content_type": content_type}
    )
    return str(video_id)
