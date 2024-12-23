# audio

This is the service that handles audio - both transcription and translations. More documentation will be here as the service is developed.

## Endpoints

1. `GET /transcriptions/{transcription_id}`

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

2. `POST /transcriptions/`

Parameters:

* `audiofile_url`: a string of the URL where the audio file should be downloaded from.
* `transcription_id`: a string of the unique ID of the audio file. This should match the ID used to find the matching video, and will then be used in this service to GET the transcription and also returned from this enpoint.

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