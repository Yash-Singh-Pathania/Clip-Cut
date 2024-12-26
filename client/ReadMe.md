## COMP41720 Distributed Systems

### Client Service Project

---

## Introduction

The **Client Service API** is a service designed to manage video uploads and streaming in distributed systems. Developed with **Spring Boot**, this microservice provides seamless integration for file storage, video metadata management, and retrieval functionalities. The Client Service is built to operate efficiently in standalone environments, while also being capable of integrating with the **Broker Service API** for advanced distributed operations.

By leveraging **OpenAPI/Swagger** support for self-documenting APIs, developers can easily explore and utilize the Client Service. The API is designed to simplify integration, asset management, and overall system scalability in distributed environments.

### Key Features

- **Comprehensive File Management**:
    - Handles video uploads, secure storage, and retrieval.
    - Provides seamless streaming support for different video formats.

- **Integrated OpenAPI Documentation**:
    - Intuitive Swagger documentation generated with **SpringDoc OpenAPI**.
    - Includes metadata such as API tags, licensing, and contacts for easy adoption.

- **Environment Ready**:
    - Preconfigured server settings for local, testing, and production deployments.

- **Lightweight Design**:
    - Built using **Java 8**, ensuring compatibility with older systems.

This project simplifies distributed file and video management through a feature-rich and scalable architecture.

---

## Project Structure
client-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── service/
│   │   │       └── service.client/
│   │   │           ├── ClientApplication.java        # Main entry point
│   │   │           ├── ClientService.java            # Core logic for video uploads and streaming
│   │   │           ├── controller/
│   │   │           │   └── ClientController.java      # REST controller providing endpoints
│   │   │           └── model/
│   │   │               ├── VideoMetadata.java        # Metadata model
│   │   │               └── UploadResponse.java       # Response model
│   │   └── resources/
│   │       ├── application.properties                # Configuration file
│   └── test/
│       ├── java/
│       │   └── service/
│       │       └── client/
│       │           └── ClientServiceTests.java       # Unit and integration test cases
├── target/                                            # Compiled application output after build
├── pom.xml                                            # Maven configuration file
├── Dockerfile                                         # Docker configuration file
└── README.md                                          # Project documentation


---

## Services

The **Client Service API** provides the following key functionalities:

1. **Video Upload and Storage**:
    - Allows users to upload video files (e.g., `.mp4`) to the local file system.
    - Automatically validates and sanitizes uploaded files for enhanced security.

2. **Video Streaming**:
    - Streams videos in byte arrays with configurable quality parameters.
    - Supports the retrieval of video files via their unique IDs.

3. **Metadata Registration**:
    - Registers video metadata with the **Broker Service** or similar management systems.

4. **API Documentation**:
    - Fully documented endpoints accessible via the integrated Swagger UI.

5. **OpenAPI Configuration**:
    - Custom `OpenAPI` (via Spring Bean) to enable dynamic API metadata generation for various environments.

---

## How to Use It

### Prerequisites:
- **Java 8** installed on your machine.
- **Maven** for building and running the project.
- A REST client, such as **Postman** or **cURL**, for interacting with the APIs.

(Optional tools based on your needs):
- **Docker** for containerized deployment.
- Video player or viewer app (e.g., VLC Media Player) to test streamed video.

---

### Steps to Setup and Run:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd client-service
   ```

2. Compile and build the project:
   ```bash
   mvn clean install
   ```

3. Run the Client Service:
   ```bash
   mvn spring-boot:run
   ```

4. Access the API at:
    - Main URL: `http://localhost:8081`
    - Swagger UI documentation: `http://localhost:8081/swagger-ui/index.html`

---

## REST Endpoints

### **Video Management**

#### 1. **POST** `/videos/upload`
- Uploads a video file to the local storage and registers it with metadata.
- **Payload Example (Multipart Form Data)**:
  ```json
  {
      "file": "<video-file>"
  }
  ```
- **Response Example**:
  ```json
  {
      "videoId": "f53a1ebd-d132-42dc-8c1f-ba8f5d1d5d15",
      "message": "Video uploaded and registered successfully"
  }
  ```

---

#### 2. **GET** `/videos/stream/{videoId}`
- Streams the video file corresponding to the unique `videoId`.
- **Path Parameters**:
    - `videoId`: The unique identifier for the video.
- **Response**:
    - Returns video data as a byte stream.

---

#### 3. **POST** `/metadata/register`
- (Optional) Registers video metadata with the Broker Service.

---

## Testing the Services

Use any REST API testing tool like **Postman** or **cURL** to test the endpoints:

- Example for video upload:
   ```bash
   curl -X POST http://localhost:8081/videos/upload \
   -F "file=@path/to/video.mp4" \
   -H "Content-Type: multipart/form-data"
   ```

- Example for streaming a video:
   ```bash
   curl -X GET http://localhost:8081/videos/stream/{videoId} \
   -o downloaded_video.mp4
   ```

---

## Docker Deployment

### Dockerfile

The Client Service includes a `Dockerfile` for containerization:

```dockerfile
# Use an official Java runtime as a parent image
FROM openjdk:8-jdk-alpine

# Set the working directory
WORKDIR /app

# Copy the application JAR file into the container
COPY target/client-service-0.0.1-SNAPSHOT.jar client.jar

# Expose port 8081 for the Client Service
EXPOSE 8081

# Command to run the application
ENTRYPOINT ["java", "-jar", "client.jar"]
```

---

### Running the Docker Container

To build and run the Docker container for the Client Service:

1. Build the Docker image:
   ```bash
   docker build -t client-service .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 8081:8081 client-service
   ```

3. Access the Client Service at `http://localhost:8081/swagger-ui/index.html`.

---

## Conclusion

The Client Service API provides a flexible and lightweight solution for video management in distributed systems. By consolidating file handling, metadata registration, and video streaming, the Client Service empowers developers to build robust distributed applications.

This API is designed with modularity and efficiency, making it a reliable choice for distributed systems requiring video storage and management capabilities.

## Contact

For any queries or feedback, please contact [sinem.taskin@ucdconnect.ie].
