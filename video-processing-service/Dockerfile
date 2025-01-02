FROM python:3.10-slim

RUN apt update && apt install -y ffmpeg libsm6 libxext6

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Define environment variable
ENV MONGO_URL=mongodb://mongodb-service:27017/video_status

# Run the application when the container launches
CMD ["python", "./service/main.py"]
