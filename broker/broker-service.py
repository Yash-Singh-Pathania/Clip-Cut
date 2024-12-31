from flask import Flask, request, jsonify
import pika
import json

# Configuration
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'video-processing-pipeline'

# Flask application setup
app = Flask(__name__)

def publish_to_queue(message):
    """
    Publishes a message to the RabbitMQ queue.

    :param message: The message to publish to RabbitMQ
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)  # Persistent message
    )
    connection.close()
    print("[Broker] Message published to queue!")

@app.route("/process", methods=["POST"])
def process_request():
    """
    API Endpoint to process video and audio data from the Client Service.
    """
    data = request.get_json()

    # Validate the incoming request
    if 'video_file_path' not in data or 'audio_file_path' not in data:
        return jsonify({"error": "Invalid request. 'video_file_path' and 'audio_file_path' are required."}), 400

    message = {
        "video_file_path": data['video_file_path'],
        "audio_file_path": data['audio_file_path']
    }

    # Publish to RabbitMQ
    try:
        publish_to_queue(message)
        return jsonify({"message": "Data received and published to RabbitMQ."}), 200
    except Exception as e:
        print(f"[Broker] Failed to publish message: {e}")
        return jsonify({"error": "Failed to process data."}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
