# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies, including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install any needed Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside the container (adjust as necessary)
EXPOSE 8000

# Define environment variables
ENV RABBITMQ_HOST=localhost
ENV RABBITMQ_PORT=5672
ENV AUDIO_SERVICE_URL=http://localhost:8000/audio/

# Run the application when the container starts
CMD ["python", "video_processing_service/service/main.py"]
