from database import db, grid_fs_bucket
from bson.objectid import ObjectId
import asyncio

async def upload_video_to_db(filename, content, content_type):
    video_id = await grid_fs_bucket.upload_from_stream(
        filename,
        content,
        metadata={"content_type": content_type}
    )
    return str(video_id)
