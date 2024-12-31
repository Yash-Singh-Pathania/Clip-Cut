import os
import subprocess
import json
import pika
import logging
import requests
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
AUDIO_SERVICE_URL = os.getenv("AUDIO_SERVICE_URL", "http://localhost:8000/audio/")  # URL for audio service

# RabbitMQ setup
def setup_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()

        # Declare required queues
        channel.queue_declare(queue="audio_processing")
        channel.queue_declare(queue="video-processing-pipeline")
        logger.info("RabbitMQ setup complete.")
        return channel
    except Exception as e:
        logger.error(f"Error setting up RabbitMQ: {e}")
        raise


# Split audio and video
def separate_audio_video(input_video_path, output_video_path, output_audio_path):
    try:
        audio_command = [
            "ffmpeg", "-i", input_video_path, "-q:a", "0", "-map", "a", output_audio_path
        ]
        subprocess.run(audio_command, check=True)

        video_command = [
            "ffmpeg", "-i", input_video_path, "-an", output_video_path
        ]
        subprocess.run(video_command, check=True)

        logger.info(f"Audio saved to {output_audio_path}, video saved to {output_video_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during audio/video separation: {e}")
        raise


# Get video resolution
def get_video_resolution(video_path):
    try:
        command = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0", "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0", video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        resolution = tuple(map(int, result.stdout.strip().split("x")))
        logger.info(f"Video resolution for {video_path}: {resolution[0]}x{resolution[1]}")
        return resolution
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting video resolution: {e}")
        raise


# Should process resolution
def should_process_resolution(input_resolution, target_resolution):
    input_width, input_height = input_resolution
    target_width, target_height = map(int, target_resolution.split("x"))
    return input_width >= target_width and input_height >= target_height


# Video processing (downscaling)
def process_video(video_path, user_id, video_id):
    resolutions = [("360p", "640x360"), ("480p", "854x480"), ("720p", "1280x720")]
    base_dir = Path(f"{user_id}/vid/{video_id}/video")
    base_dir.mkdir(parents=True, exist_ok=True)

    input_resolution = get_video_resolution(video_path)

    for res_name, res_dim in resolutions:
        if should_process_resolution(input_resolution, res_dim):
            output_path = base_dir / res_name / f"{res_name}.mp4"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                command = [
                    "ffmpeg", "-i", video_path, "-vf",
                    f"scale=w='if(gt(iw,{res_dim.split('x')[0]}),{res_dim.split('x')[0]},iw)':h='if(gt(ih,{res_dim.split('x')[1]}),{res_dim.split('x')[1]},ih)'",
                    "-c:v", "libx264", "-crf", "23", "-preset", "fast", str(output_path)
                ]
                subprocess.run(command, check=True)
                logger.info(f"{res_name} video saved at {output_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error processing {res_name}: {e}")
        else:
            logger.info(f"Skipping {res_name}, as input resolution is too low.")


def push_audio_to_service(audio_path, user_id, video_id):
    try:
        audiofile_url = f"http://localhost:8000/audio/{audio_path}"  # Replace with appropriate URL
        audio_service_url = AUDIO_SERVICE_URL
        payload = {"audiofile_url": audiofile_url, "user_id": user_id, "video_id": video_id}
        response = requests.post(audio_service_url, json=payload)

        # Call raise_for_status to trigger an error for unsuccessful status codes
        response.raise_for_status()

        logger.info(f"Successfully pushed audio to Audio Service for video {video_id} (user {user_id})")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error pushing audio to service: {e}")
        raise


# RabbitMQ message handling
def handle_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        user_id = message["user_id"]
        video_id = message["video_id"]
        video_path = message["video_path"]

        output_audio_path = f"{user_id}/vid/{video_id}/audio/audio.mp3"
        output_video_path = f"{user_id}/vid/{video_id}/video/video_no_audio.mp4"

        separate_audio_video(video_path, output_video_path, output_audio_path)
        process_video(output_video_path, user_id, video_id)

        # Push audio to the audio service
        push_audio_to_service(output_audio_path, user_id, video_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Successfully processed video {video_id} for user {user_id}.")
    except Exception as e:
        logger.error(f"Error handling message: {e}")


# Main
def main():
    try:
        channel = setup_rabbitmq()
        channel.basic_consume(queue="video-processing-pipeline", on_message_callback=handle_message)
        logger.info("Waiting for messages...")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Cleaned up resources.")


if __name__ == "__main__":
    main()
