# video-processing-service

Service that processes uploaded videos, ie rescales them to various resolutions and stores these in the database. Has no endpoints, simply listens to a Redis pub/sub channel.