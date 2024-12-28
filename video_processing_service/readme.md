Listens to video-processing-pipeline queue to receive the audio
1. Split audio to 'audio_processing' queue, is what the audio service listens to.
2. Process Video 
    1. Make three qualities 
        1. 480p 
        1. 360p 
        1. 720p
    1. If video is of lower quality do not upscale it 
Save these videos in local file path the file path would be as following 
uuid(user)/vid(video id )/video/360p,480p,720

Developer : Nishal