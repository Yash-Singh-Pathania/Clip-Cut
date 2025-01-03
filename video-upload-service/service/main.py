from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import init_mongo, upload_video_to_db
import redis

REDIS_CHANNEL = "video_uploads"

app = FastAPI()

# Configure CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

redis_channel = redis.StrictRedis(host="redis-service", port=6379)

# -------------------------------------------------------------------------
# Startup event: init Mongo BEFORE handling requests
# -------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB connection and GridFS
    await init_mongo()

# -------------------------------------------------------------------------
# Video upload endpoint
# -------------------------------------------------------------------------
@app.post("/upload-video/")
async def upload_video(user_id: str, file: UploadFile = File(...)):
    print(f"{user_id} uploading {file.filename}")

    tagged_filename = f"{user_id}_{file.filename}"
    contents = await file.read()

    # Example size limit (100 MB)
    if len(contents) > 100 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    print(f"Uploading {file.filename} to DB")
    video_id = await upload_video_to_db(tagged_filename, contents, file.content_type, user_id)

    print(f"Publishing {tagged_filename},{video_id} to Redis channel")
    redis_channel.publish(REDIS_CHANNEL, f"{tagged_filename},{video_id}")

    return {"filename": file.filename, "video_id": video_id}
