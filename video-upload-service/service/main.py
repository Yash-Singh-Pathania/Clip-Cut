from fastapi import FastAPI, File, UploadFile, HTTPException
from .database import upload_video_to_db
import redis

REDIS_CHANNEL = "video_uploads"

app = FastAPI()
redis_channel = redis.StrictRedis(host="redis-service", port=6379)


@app.post("/upload-video/")
async def upload_video(user_id: str, file: UploadFile = File(...)):
    print(f"{user_id} uploading {file.filename}")

    tagged_filename = f"{user_id}_{file.filename}"
    contents = await file.read()
    if len(contents) > 100 * 1024 * 1024:  # Check for 100MB size limit
        raise HTTPException(status_code=413, detail="File too large")

    print(f"Uploading {file.filename} to DB")
    video_id = await upload_video_to_db(tagged_filename, contents, file.content_type)

    print(f"Publishing {tagged_filename},{video_id} to Redis channel")
    redis_channel.publish(REDIS_CHANNEL, f"{tagged_filename},{video_id}")    

    return {"filename": file.filename, "video_id": video_id}
