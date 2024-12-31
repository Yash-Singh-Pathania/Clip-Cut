import redis, cv2
import ffmpeg
from app.config import settings
from enum import Enum

# Enum to represent video resolutions
class VideoResolution(Enum):
    _1080P = (1920, 1080)
    _720P = (1280, 720)
    _480P = (640, 480)
    _360P = (480, 360)
    _240P = (320, 240)

    @classmethod
    def get_dimensions(cls, resolution_name: str):
        resolution = cls[resolution_name]
        return resolution.value


def compress_video(input_path: str, output_path: str, resolution_name: str):

    width, height = VideoResolution.get_dimensions(resolution_name)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {input_path}")
        return
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height)) 
    
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        resized_frame = cv2.resize(frame, (width, height))
        
        out.write(resized_frame)
        
    cap.release()
    out.release()
    print(f"Video processed and saved to: {output_path}")



def process_videos():
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    pubsub = r.pubsub()
    pubsub.subscribe(settings.redis_channel)

    print(f"Subscribed to Redis channel: {settings.redis_channel}")

    for message in pubsub.listen():
        if message["type"] == "message":
            video_data = message["data"]
            print("Received video for processing.")

            input_path, output_path, quality = video_data.decode("utf-8").split(",")
            
            if quality not in VideoResolution.__members__:
                print(f"Error: Invalid resolution name: {quality}")
                continue

            try:
                compress_video(input_path, output_path, quality)
                print(f"Video processed and saved to: {output_path}")
            except Exception as e:
                print(f"Error processing video: {e}")
