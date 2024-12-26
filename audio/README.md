# audio

This is the service that handles audio - both transcription and translations. More documentation will be here as the service is developed.

## Prerequisites

`ffmpeg` must be installed.

macOs:

```bash
$ brew install ffmpeg
```

Linux:

```bash
$ sudo apt install ffmpeg
```

## Endpoints

1. `GET /audio/transcription/{video_id}`

Get the transcription stored at the given ID. The JSON returned is in the form

```json
[
  {
    "timestamp": {
      "start": 0,
      "end": 0
    },
    "text": "string"
  }
]
```

2. `GET /audio/audiofile/{video_id}`

Get an MP3 streaming response to the audio stored with the given ID.

3. `POST /audio/`

Parameters:

* `audiofile_url`: a string of the URL where the audio file should be downloaded from.
* `video_id`: a string of the unique ID of the audio file. This should match the ID used to find the matching video, and will then be used in this service for the GET endpoints and also returned from this enpoint.

Have this service download the audio file, convert it to a 320kbps MP3 and store it. The converted audio is transcribed and then the transcription and the converted audio is made available through this service's GET endpoints.

## Development

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

You should then reactivate the virtual environment so the correct `pytest` is used.

```bash
$ deactivate && source .venv/bin/activate
```

## Running

```bash
$ fastapi dev service/main.py
```

Visit [127.0.0.1:8000/docs#/](http://127.0.0.1:8000/docs#/) for Swagger UI.

## Testing

Also in the same virtual environment:

```bash
$ pytest
```
