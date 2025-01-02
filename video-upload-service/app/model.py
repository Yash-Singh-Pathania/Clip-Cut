from database import grid_fs_bucket

async def upload_video_to_db(filename, content, content_type, user_id, video_type="original"):
    """
    Upload a video to GridFS with metadata for user_id and type.
    Default type is 'original'.
    """
    video_id = await grid_fs_bucket.upload_from_stream(
        filename,
        content,
        metadata={
            "content_type": content_type,
            "user_id": user_id,
            "type": video_type
        }
    )
    return str(video_id)
