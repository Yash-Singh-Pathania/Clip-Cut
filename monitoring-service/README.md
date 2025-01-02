# video-upload-service

Service that handles video uploading.

## Endpoints

`POST /upload-video`

Parameters:

1. `user_id`: ID of the user uploading the video.
2. `file`: Local file to be uploaded.

Uploads the raw video to the database, then publishes to the Redis channel to notify the processing service to process the video.