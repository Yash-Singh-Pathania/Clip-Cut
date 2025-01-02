from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from model import upload_video_to_db
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-video/")
async def upload_video(
    user_id: int = Form(...), 
    file: UploadFile = File(...),
):
    # Validate file size
    contents = await file.read()
    if len(contents) > 100 * 1024 * 1024:  # 100MB limit
        raise HTTPException(status_code=413, detail="File too large")

    video_id = await upload_video_to_db(
        filename=file.filename,
        content=contents,
        content_type=file.content_type,
        user_id=user_id,
        video_type="original"
    )

    return {"filename": file.filename, "video_id": video_id, "user_id": user_id}
