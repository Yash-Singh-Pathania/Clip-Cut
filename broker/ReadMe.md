## COMP41720 Distributed Systems

### Distributed Systems Project

---

## Introduction

The **Broker Service API** is a microservice designed to act as a key intermediary in distributed systems, facilitating communication, resource distribution, and streamlined API management. Built using **Spring Boot**, this service provides a robust framework for creating and managing RESTful APIs, empowering developers with comprehensive functionality and clear documentation.

With integrated **OpenAPI/Swagger** support, the Broker Service ensures fully documented APIs, fostering transparency and better usability for both developers and clients. This microservice caters to various operational needs such as **broker operations** and **account management**, while supporting deployment across multiple environments such as local, development, and production.

Key features include:

- **Comprehensive API Documentation**:
    - Generated using **SpringDoc OpenAPI**, accessible via the Swagger UI.
    - Includes metadata such as licensing, contact details, and external links for technical documentation.

- **Multi-Environment Support**:
    - Preconfigured server definitions for local, development, and production environments.

- **Scalable Configuration**:
    - Categorized API endpoints using tags for better organization and usability.

- **Lightweight and Java 8 Compatible**:
    - Developed with Java 8, making it suitable for environments where upgrading Java versions isn't feasible.

This project aims to simplify distributed system development by offering a well-documented, easy-to-use API powered by modern design principles and best practices.

---
## Project Structure
src/
├── main/
│   ├── java/
│   │   └── service/
│   │       └── broker/
│   │           ├── BrokerApplication.java        # Main entry point of the application
│   │           ├── brokerService.java            # OpenAPI configuration for API documentation
│   │           ├── controller/                   # Contains all the REST controllers
│   │           ├── service/                      # Service layer where business logic is implemented
│   │           └── model/                        # Data transfer objects (DTOs) and entity classes
│   └── resources/
│       ├── application.properties                # Application configuration file
│       └── static/                               # Static resources such as Swagger-UI customizations (if any)
└── test/
└── java/
└── service/
└── broker/
└── BrokerServiceTests.java       # Unit and integration test cases

## Services

The **Broker Service API** provides the following key services to support distributed system functionality:

1. **Broker Operations**:
    - Manages routing and distribution of brokered requests.
    - Facilitates efficient communication between systems.

2. **Account Management**:
    - Handles account-related activities, such as creation, updates, and deletions.
    - Guarantees secure access and processing of user account data.

3. **API Documentation**:
    - Explore API details via the integrated Swagger UI (OpenAPI).
    - Automatically generated documentation includes tags, metadata, and sample responses.

4. **Service Registration**:
    - Dynamically registers backend quotation services with the Broker Service via REST endpoints.

---
---

## How to Use It

### Prerequisites:
- **Java 8** installed on your machine.
- **Maven** for building and running the project.
- A REST client, such as **Postman** or **cURL**, for interacting with the APIs.
- (Optional) **Docker** for containerized deployment.

### Steps to Setup and Run:
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd lifeco-rest/broker
   ```

2. Compile and build the project:
   ```bash
   mvn clean install
   ```

3. Run the Broker Service:
   ```bash
    mvn compile spring-boot:run -pl broker
   ```

4. Access the API at:
    - Main URL: `http://localhost:8080`
    - Swagger UI documentation: `http://localhost:8080/swagger-ui/index.html`

---

## REST Endpoints

### **Application Management**
1. **POST** `/applications`
    - Create a new application consisting of `ClientInfo` and a list of quotation URLs.
    - **Payload Example**:
      ```json
      {
          "clientInfo": {
              "name": "John Doe",
              "age": 35,
              "license": "Full"
          },
          "quotationUrls": [
              "http://localhost:8080/quotations",
              "http://localhost:8081/quotations"
          ]
      }
      ```
    - **Response Example**:
      ```json
      {
          "applicationId": 1,
          "message": "Application created successfully!"
      }
      ```

2. **GET** `/applications`
    - Retrieve all existing applications.

3. **GET** `/applications/{id}`
    - Retrieve a specific application using its unique ID.

---

### **Service Registration**
1. **POST** `/services`
    - Dynamically register backend quotation services with the Broker Service.
    - **Payload Example**:
2. **GET** `/services`
    - Retrieve a list of all registered quotation services.

---

## Testing the Services

You can test the Broker Service RESTful endpoints using:
- **Postman**: For GUI-based REST API testing.
- **cURL**: Command-line tool for interacting with APIs.
    - Example:
      ```bash
      curl -X POST http://localhost:8083/applications \
      -H "Content-Type: application/json" \
      -d '{"clientInfo": {"name": "Jane Doe", "age": 29, "license": "Full"}, "quotationUrls": ["http://example.com/quotation1"]}'
      ```

---

## Docker Deployment

### Dockerfile

The Broker Service includes a `Dockerfile` for containerization:
```dockerfile
# Use an official Java runtime as a parent image
FROM openjdk:8-jdk-alpine

# Set the working directory
WORKDIR /app

# Copy the application JAR file into the container
COPY target/broker-0.0.1-SNAPSHOT.jar broker.jar

# Expose port 8083 for the Broker Service
EXPOSE 8080

# Command to run the application
ENTRYPOINT ["java", "-jar", "broker.jar"]
```

### Running the Docker Container

To build and run the Docker container for the Broker Service:

1. Build the Docker image:
   ```bash
   docker build -t broker-service .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 8080:8080 broker-service
   ```

3. Access the Broker Service at `http://localhost:8080`.

---

## Conclusion

The Broker Service is designed to streamline communication in distributed systems, acting as a centralized hub to register and manage services while providing easy-to-use RESTful APIs. Its modular and independent design ensures scalablity, flexibility, and ease of use for developers working in distributed environments.

## Contact

For any queries or issues, please contact [sinem.taskin@ucdconnect.ie].