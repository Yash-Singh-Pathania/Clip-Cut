## Broker Service
## Overview
The Broker Service serves as a middleware to handle communication between the Video Upload Service and the Video Processing Service. It consumes messages from a RabbitMQ queue (video-processing-pipeline), processes video and audio data, and delegates tasks to the respective services.
## Features
## Message Handling:
Consumes messages from the video-processing-pipeline queue in RabbitMQ.
Processes video/audio file paths.
## Communication with Services:
Sends audio data to the Audio Processing Service.
Sends video data to the Video Processing Service.
## Error Handling:
Proper handling of invalid message formats or service failures.
## Scalability:
Supports persistent messaging in RabbitMQ to ensure reliability.

## Technologies Used
Python: Used for writing the Broker Service logic.
RabbitMQ: Message broker for queue handling.
Libraries:
pika: Handles RabbitMQ operations in Python.
requests: Makes HTTP requests to the processing services.
json: Encodes/decodes data messages.

## Prerequisites
## RabbitMQ:
Ensure RabbitMQ is installed and running on your system.
Enable the RabbitMQ Management UI (Optional):

```sh
rabbitmq-plugins enable rabbitmq_management
```
## Python:
Install Python 3.8+ on your operating system. Hyperlink removed for security reasons.
Install Dependencies:
Python libraries pika and requests are required. Install them with:
```sh
pip install pika requests
```
## Installation
Clone the Repository:
```sh
git clone <repo_url>
cd broker-service
```
## Install Dependencies:
```sh
pip install -r requirements.txt
```
## How to Run the Broker Service
```sh
rabbitmq-service.bat start
```
## Run the Broker Service: Execute the broker_service.py script:
```sh
python broker_service.py
```
The service will start consuming messages from the video-processing-pipeline queue. You should see the following output:
[Broker] Waiting for messages in queue: video-processing-pipeline...

## How to Use the Broker Service 

Send a Test Message: Publish a test message to the video-processing-pipeline queue to simulate video and audio processing.

Verify Communication with Processing Services:

The Audio Service should receive the audio_file_path and start processing.
The Video Service should receive the video_file_path and start processing.

## Inspect RabbitMQ:
Open the RabbitMQ Management UI at Hyperlink removed for security reasons.
Verify that the message was consumed from the video-processing-pipeline queue.

## Configuration

RabbitMQ Configuration in broker_service.py:
Host:
RABBITMQ_HOST: Specify the RabbitMQ hostname. Defaults to localhost.
Queue Name:
UPLOAD_QUEUE: Defaults to video-processing-pipeline.
External Services:
URLs for Services:
VIDEO_PROCESSING_SERVICE_URL: Endpoint for the Video Processing Service.
AUDIO_SERVICE_URL: Endpoint for the Audio Service.

## API Message Format
The Broker Service expects messages in the following JSON format:
{
  "audio_file_path": "/path/to/audio/file.mp3",
  "video_file_path": "/path/to/video/file.mp4"
}

## Error Handling
Invalid Messages:
The service will reject invalid messages (e.g., with missing fields) and log the error.
Service Failures:
If the Audio or Video Service fails, the error is logged and the message will not be retried.
RabbitMQ Issues:
If RabbitMQ is unreachable, the broker will throw an error. Ensure RabbitMQ is running before starting the service.

## Logging and Monitoring
Logs:
All processing and delegation-related activities are logged to the console (stdout).
Monitoring RabbitMQ:
Monitor RabbitMQ queue health via the RabbitMQ Management UI at Hyperlink removed for security reasons.
Database Tracking:
Maintain a PostgreSQL table to keep track of all videos currently being processed and their status:
Columns:
Video ID
Current Status (e.g., processing, completed, or failed)
Extend the code base if you’d like to integrate the database.

## Future Enhancements
Cloud Integration:
Add support for cloud storage solutions like Amazon S3.
Retry Mechanisms:
Add retries to handle failures in processing.
Multiple Queue Support:
Expand the service to support additional queues and routes for various tasks.
## Contributing
Fork the repository.
Create a new branch and add your feature or fix.
Submit a pull request for review.
We welcome contributions to enhance the reliability and functionality of the Broker Service.

## Contact

For any queries or issues, please contact [sinem.taskin@ucdconnect.ie].