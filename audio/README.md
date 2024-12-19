# audio

This is the service that handles audio - both transcription and translations. More documentation will be here as the service is developed.

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

```bash
$ pytest
```