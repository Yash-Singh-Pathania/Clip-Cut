## Client Service
## Overview
The Client Service enables users to submit video and audio file metadata (file paths) to the Broker Service. This metadata is then processed by the Broker Service, which interacts with RabbitMQ to enqueue the tasks for downstream processing services.
The Client Service is designed to ensure seamless communication between the client (user) and the backend service.
## Features
1) Integration with the Broker Service:
- Sends video and audio file metadata to the Broker Service via an HTTP POST request.
- Ensures that input JSON is structured and correctly validated.
2) Ease of Use:
- Allows users to easily specify video and audio file paths.
- Handles errors such as network issues, invalid input data, or inaccessible Broker Service.
3) Simple Configuration:
- Set the Broker Service URL via configuration.
- Easily update and extend to handle additional metadata fields.

## Technologies Used
Python 3.8+
Requests: A lightweight HTTP library used for making API calls to the Broker Service.

## Prerequisites
Python: Ensure Python 3.8 or higher is installed. You can download Python Hyperlink removed for security reasons.
Broker Service: Start the Broker Service before using the Client Service. Refer to the Hyperlink removed for security reasons for setup instructions.

## Installation
Clone the Repository:
```sh
git clone <repo_url>
cd client-service
```
Set Up Virtual Environment (Recommended): Create and activate a Python virtual environment:
```sh
python -m venv venv
source venv/bin/activate     # For macOS/Linux
venv\Scripts\activate        # For Windows
```
Install Dependencies: Install the required Python modules:
```sh 
pip install -r requirements.txt
```
## How to Run the Client Service
Open the client_service.py file and edit the following line to specify the Broker Service URL:

```sh
BROKER_SERVICE_URL = "http://localhost:5000/process"
```
Run the script:
```sh
python client_service.py
```
The script will submit sample metadata to the Broker Service, and you will see the console logs indicating the results.

## How to Use the Client Service
Modify File Paths: Update the file paths in the client_service.py script to point to the correct locations of your video and audio files:
```sh
video_file = "/path/to/video/file.mp4"
audio_file = "/path/to/audio/file.mp3"
```

- Send Request to Broker Service: When you run the script, the Client Service will:
Validate the file paths in its payload.
Send a POST request to the Broker Service by default to:
```sh
http://localhost:5000/process
```
Example Output: On successful execution, you should see:
[Client] Sending request to Broker Service...
[Client] Successfully sent data to Broker Service!
[Client] Response: {"message": "Data received and published to RabbitMQ."}

If there are any issues, the script will print an appropriate error message.
## Configuration
- You can configure the following in client_service.py:
Broker Service URL: Default:
```sh
BROKER_SERVICE_URL = "http://localhost:5000/process"
```
Change it to the hostname or IP address where the Broker Service is running, if not on the default localhost.

- Video and Audio Files: Update these variables with the paths to your files:
```sh
video_file = "/path/to/video/file.mp4"
audio_file = "/path/to/audio/file.mp3"
```
## Error Handling
- Network-Related Errors:
If the Broker Service is unreachable, the script will print an error:
[Client] Error occurred: ConnectionError or Timeout  

- Invalid Response:
If the Broker Service returns an error (e.g., invalid request), the error will be logged:
[Client] Failed to send data. HTTP 400: {"error": "..."}

-File Path Errors:
Ensure that the file paths you provide are accessible to prevent workflow disruptions.

## Directory Structure
The directory for the Client Service should look like this:
client-service/
├── client_service.py      # The Client Service code
├── requirements.txt       # Python dependencies
└── README.md              # This documentation

## Example Interaction with Broker Service
Request Sent (By Client Service):
```sh
{
    "video_file_path": "/path/to/video/file.mp4",
    "audio_file_path": "/path/to/audio/file.mp3"
}
```
- Response Received (From Broker Service)

```sh
{
    "message": "Data received and published to RabbitMQ."
}
```
## Testing the Client Service
Run the Script: Execute the Client Service script with default or modified configurations:
```sh
python client_service.py
```
- Verify Broker Logs: Check the Broker Service logs to ensure the data was received and queued into RabbitMQ.
Inspect RabbitMQ: Use the RabbitMQ Management UI at Hyperlink removed for security reasons to confirm the message was queued in video-processing-pipeline.

## Future Enhancements
Add support for uploading additional metadata along with video/audio paths.
Extend scripts to allow direct file uploads (instead of paths).
Implement retries for failed requests based on HTTP response codes.

## Contributing
- We welcome contributions to improve the Client Service.
- Steps to Contribute:
- Fork the repo.
- Create a branch (feature-xyz).
- Add your feature or fix.
- Submit a pull request for review.

## Contact

For any queries or issues, please contact [sinem.taskin@ucdconnect.ie].