FROM python:3

RUN apt update
RUN apt update && apt install -y ffmpeg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "fastapi", "run", "service/main.py" ]
