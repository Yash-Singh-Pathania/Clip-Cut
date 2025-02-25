

"Clip Cut" Video Streaming Service
Check out the tech emo here : https://www.youtube.com/watch?v=ZEbcFXgoI5Q 

A distributed and scalable video streaming service. Users can create accounts, upload videos, and stream videos with a desired quality as well as automatically generated subtitles. The service runs in a Kubernetes cluster to ensure scalability and fault-tolerance. It employs a microservice architecture with the various services written in Python, mostly with FastAPI, communicating with either REST or Redis pub/sub channels, and a React frontend.

## Running
TLDR : if you have docker and minikube 

Running this command alone should set everything up 
'''code
chmod +x clip_cut.sh ./clip_cut.sh
'''
---- 

Install Docker, Kubernetes and Minikube.

MacOS/Linux:

```bash
$ sudo chmod +x run.sh
$ ./run.sh
```

Do not run as `sudo`. You will be prompted for your password only to run the tunnel.

Windows (Powershell with Administrator privileges):

```bash
$ ./run.ps1
```

Keep this terminal window open (it takes a long time to start!).

To check the status of the services, in a different terminal run:

```bash
$ minikube dashboard
```

SwaggerUI docs for the user-facing services (`user-service` and `video-upload-service`) can be found at http://127.0.0.1:80/docs# and http://127.0.0.1:81/docs#, respectively.

To inspect the contents of the MongoDB database, either open a shell in the MongoDB instance:

```bash
$ POD_NAME=$(kubectl get-pods --no-headers -o custom-columns=":metada.name" | grep mongodb)
$ kubectl exec --stdin --tty $POD_NAME -- /bin/bash
```

Or port-forward to inspect using MongoDB Compass:

```bash
$ POD_NAME=$(kubectl get-pods --no-headers -o custom-columns=":metada.name" | grep mongodb)
$ kubectl port-forward $POD_NAME 27017:27017
```


## User-Facing Services

1. `user-service`

This service, accessed via the frontend, is a FastAPI app responsible for managing user account creating, login, and management. It uses PostgreSQL for user accounts.

2. `video-upload-service`

Also a FastAPI app, this service adds a user-provided file to the MongoDB database. It then publishes to a Redis channel to notify the processing services to process the video.

## Other Services

1. `audio-service`

Another FastAPI app that uses the pretrained OpenAI whisper-tiny model to transcribe a user-uploaded video and return the transcription JSON through a REST API. In a production scenario, a better but much larger model like whiser-base could be used on a dedicated TPU machine.

2. `video-processing-service`

After this service is notified from the Redis channel that a video has been uploaded, it gets the transcription from the audio service and uses `ffmpeg` to rescale the video to different resolutions and store the rescaled copies in the MongoDB database.

3. `monitoring-service`

A FastAPI app that monitors video uploads and stores their IDs in a PostgreSQL database for quick lookup and querying from users.

4. `mongo-service`, `postgres-service` and `redis-service`

These services contain no code, but are configured to run Docker images for the appropriate technologies in the Kubernetes cluster.
