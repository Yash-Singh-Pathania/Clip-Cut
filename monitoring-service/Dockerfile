# Use Python 3.10 slim image from Docker Hub
FROM python:3.10-slim

# Copy the requirements file into the container
COPY requirements.txt ./

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose port 8001 on the container
EXPOSE 8002

# Set environment variables
ENV POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/video_status

# Command to run the application using Uvicorn
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8002"]
