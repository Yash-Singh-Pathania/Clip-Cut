FROM python:3.10-slim

RUN apt update && apt install -y ffmpeg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY service/ /service/
COPY whisper-tiny/ /whisper-tiny/

ENV MONGO_URL=mongodb://mongodb-service.default.svc.cluster.local:27017/video_status

EXPOSE 8000
# CMD [ "fastapi", "run", "service/main.py" ]
CMD ["fastapi", "run", "service/main.py"]