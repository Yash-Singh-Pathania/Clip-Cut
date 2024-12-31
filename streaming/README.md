# streaming

This service provides video streaming.

## Endpoints

`GET /streaming/{user_id}/{video_id}/`

Parameters:

* `quality`: requested quality of the video (480p, 720p, etc)
* `lang`: requested language of the audio and subtitles ('en', etc)

The service retrieves the requested video, audio and subtitles from the other relevant services and combines them into a single MP4 video which is streamed back to the caller through a streaming response.

## Development

### Prerequisites

Please use Python 3.8 for dependency consistency!

`ffmpeg` must be installed.

macOs:

```bash
$ brew install ffmpeg
```

Linux:

```bash
$ sudo apt install ffmpeg
```

First, ensure you are working in a virtual environment.

```bash
$ cd audio
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Then, install necessary dependencies.

```bash
$ python3 -m pip install -r requirements.txt
```

### Running

```bash
$ fastapi dev service/main.py
```

Visit [127.0.0.1:8000/docs#/](https://127.0.0.1:8000/docs#/) for Swagger UI.

## Developer

Ryan Jeffares