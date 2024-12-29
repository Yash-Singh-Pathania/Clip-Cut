# Video Processing Service

## Overview

This service listens to the `video-processing-pipeline` queue to receive video and audio data. It then processes the video by splitting the audio into the `audio_processing` queue, which is consumed by the audio service. The video is processed to generate three different resolutions (480p, 360p, and 720p). Videos that are of lower quality are not upscaled. The processed video is saved in a local file system with the following directory structure.

## Features

- **Audio Handling**:
  - Splits the audio from the received video and sends it to the `audio_processing` queue for further processing by the audio service.
  - The audio service listens to the `audio_processing` queue and processes the audio file. 
  - The audio files can be accessed by the audio service at the following path:
    ```
    uuid(user)/vid(video_id)/audio/en.mp3
    ```

- **Video Processing**:
  - Makes three versions of the video:
    - **360p**
    - **480p**
    - **720p**
  - If the video is of lower quality, it will not be upscaled.
  - The processed videos are saved in a local file system at the following paths:
    ```
    uuid(user)/vid(video_id)/video/360p
    uuid(user)/vid(video_id)/video/480p
    uuid(user)/vid(video_id)/video/720p
    ```

## Requirements

- **Python 3.8+**
- **FFmpeg** (for video processing)
- **Pydub** (for audio processing)
- **FastAPI** (for service handling)
- **aiofiles** (for async file handling)
- **transformers** (for audio transcription)
- **requests** (for sending HTTP requests)

## Installation

1. Clone this repository:
    ```bash
    git clone <repo_url>
    ```

2. Install the necessary Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure you have FFmpeg installed for video processing. You can install it via the package manager or download it from [FFmpeg's official website](https://ffmpeg.org/download.html).

4. Set up and configure the necessary environment variables or configuration files, including the URL for the audio service.

## Usage

1. **Listening to the Queue**:
   - This service listens to the `video-processing-pipeline` queue for incoming video data.
   - Upon receiving a video, it processes the video and splits the audio into the `audio_processing` queue for the audio service.

2. **Video Processing**:
   - The video is processed to generate three resolutions: 480p, 360p, and 720p.
   - Videos that are of lower quality will not be upscaled.

3. **Saving Processed Videos**:
   - The processed videos are saved in a local folder following this directory structure:
     ```
     uuid(user)/vid(video_id)/video/360p
     uuid(user)/vid(video_id)/video/480p
     uuid(user)/vid(video_id)/video/720p
     ```

4. **Audio Processing**:
   - The audio is split and sent to the `audio_processing` queue, where it is consumed by the audio service.
   - The audio service can access the audio file at the following path:
     ```
     uuid(user)/vid(video_id)/audio/en.mp3
     ```

5. **Accessing Transcription**:
   - Transcriptions of the audio can be accessed at the following path:
     ```
     uuid(user)/vid(video_id)/transcription/en.json
     ```

## Example Flow

1. **Receive Video**: The service listens to the `video-processing-pipeline` queue for incoming video data.
2. **Split Audio**: The audio is extracted from the video and sent to the `audio_processing` queue for transcription and processing by the audio service.
3. **Process Video**: The video is processed into three versions (360p, 480p, and 720p).
4. **Save Processed Videos**: The processed videos are saved in a local directory:
    ```
    uuid(user)/vid(video_id)/video/360p
    uuid(user)/vid(video_id)/video/480p
    uuid(user)/vid(video_id)/video/720p
    ```
5. **Audio Service**: The audio file is saved to the following path, and the audio service can access it for processing:
    ```
    uuid(user)/vid(video_id)/audio/en.mp3
    ```

## Notes

- Ensure that the **audio service** is running and properly configured to consume the `audio_processing` queue.
- Make sure that the `AUDIO_SERVICE_URL` is correctly set to point to the running audio service.

## Developer

- **Nishal**