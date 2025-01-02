FROM python:3.8

RUN apt update && apt install -y ffmpeg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Define environment variable
ENV MONGO_URL=mongodb://mongodb-service:27017/video_status

EXPOSE 8000
CMD [ "fastapi", "run", "service/main.py" ]