import requests
import json

# Configuration
BROKER_SERVICE_URL = "http://localhost:5000/process"  # URL of the Broker Service API endpoint

def send_video_audio_data(video_path, audio_path):
    """
    Sends video and audio file data to the Broker Service.

    :param video_path: Path to the video file
    :param audio_path: Path to the audio file
    """
    headers = {'Content-Type': 'application/json'}
    payload = {
        "video_file_path": video_path,
        "audio_file_path": audio_path
    }

    try:
        print("[Client] Sending request to Broker Service...")
        response = requests.post(BROKER_SERVICE_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            print("[Client] Successfully sent data to Broker Service!")
            print("[Client] Response: ", response.json())
        else:
            print(f"[Client] Failed to send data. HTTP {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[Client] Error occurred: {e}")

if __name__ == "__main__":
    # Example usage of the Client Service
    video_file = "/path/to/video/file.mp4"
    audio_file = "/path/to/audio/file.mp3"

    send_video_audio_data(video_file, audio_file)