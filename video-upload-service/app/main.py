from fastapi import FastAPI, File, UploadFile, HTTPException
from model import upload_video_to_db
import redis

REDIS_CHANNEL = "video_uploads"

app = FastAPI()

redis_queue = redis.StrictRedis(host="redis", port=6379)


@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > 100 * 1024 * 1024:  # Check for 100MB size limit
        raise HTTPException(status_code=413, detail="File too large")
    video_id = await upload_video_to_db(file.filename, contents, file.content_type)
    redis_queue.publish(REDIS_CHANNEL, video_id)
    return {"filename": file.filename, "video_id": video_id}
