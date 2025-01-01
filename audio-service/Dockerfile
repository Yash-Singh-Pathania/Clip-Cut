FROM python:3.10-slim

RUN apt update && apt install -y ffmpeg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD [ "fastapi", "run", "service/main.py" ]