import subprocess
import tempfile

import aiofiles
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import requests

app = FastAPI()


def get_transcription(transcription_url: str) -> str:
    response = requests.get(transcription_url)
    transcription = response.json()

    srt_lines = []
    for idx, entry in enumerate(transcription, start=1):
        start: float = entry["timestamp"][0]
        end: float = entry["timestamp"][1]
        text: str = entry["text"]

        def to_srt_time(seconds: float) -> str:
            milliseconds = int((seconds - int(seconds)) * 1000)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

        srt_lines.append(
            f"{idx}\n{to_srt_time(start)} --> {to_srt_time(end)}\n{text}\n"
        )

    return "\n".join(srt_lines)


def stream_from_url(url: str):
    response = requests.get(url, stream=True)
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            yield chunk


async def stream_from_file(file_path: str):
    chunk_size = 1024
    async with aiofiles.open(file_path, mode="rb") as f:
        while chunk := await f.read(chunk_size):
            yield chunk


def merge_streams(video_url: str, audio_url: str, subtitles: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as subtitle_file:
        subtitle_file.write(subtitles.encode("utf-8"))
        subtitle_path = subtitle_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as video_file:
        video_path = video_file.name

    # fmt: off
    ffmpeg_process = subprocess.Popen(
        [
            "ffmpeg",
            "-y", # overwrite automatically
            "-i", video_url, # input 1 (video) from stdin        
            "-i", audio_url, # input 2 (audio) from stdin (another pipe)            
            "-vf", f"subtitles={subtitle_path}", # add subtitles            
            "-c:v", "libx264", # copy video codec            
            "-c:a", "aac", # encode audio to AAC            
            "-f", "mp4", # output an mp4            
            video_path, # output to tempfile we made
        ],
        stdout=subprocess.PIPE,
        pass_fds=(3,),
    )
    # fmt: on

    ffmpeg_process.wait()
    return stream_from_file(video_path)


@app.get(
    "/streaming/{user_id}/{video_id}/",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"video/mp4": {}},
            "description": "MP4 video file stream",
        },
    },
)
def stream_video(user_id: str, video_id: str, quality: str, lang: str) -> StreamingResponse:
    transcription_url = (
        f"http://localhost:8000/audio/transcription/{user_id}/{video_id}/{lang}"
    )
    # TODO: whatever the video endpoint is
    video_url = f"http://localhost:5672/video/{user_id}/{video_id}/{quality}"
    audio_url = f"http://localhost:8000/audio/audio/{user_id}/{video_id}/{lang}"

    return StreamingResponse(
        merge_streams(video_url, audio_url, transcription_url), media_type="video/mp4"
    )
