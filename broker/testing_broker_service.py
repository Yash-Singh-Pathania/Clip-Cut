import pika
import json

# Set up the RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='video-processing-pipeline', durable=True)

# Define the message to send
message = {
    "audio_file_path": "/path/to/audio/file.mp3",
    "video_file_path": "/path/to/video/file.mp4"
}

# Publish the message to the queue
channel.basic_publish(
    exchange='',
    routing_key='video-processing-pipeline',
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
)

print("Message sent!")
connection.close()  
