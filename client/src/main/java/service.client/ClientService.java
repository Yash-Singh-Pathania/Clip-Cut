package service.client;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.parameters.RequestBody;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.models.ExternalDocumentation;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.tags.Tag;
import model.UploadResponse;
import model.VideoMetadata;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;

@Service
public class ClientService {

    @Value("${video.storage.path:videos/}")
    private String videoStoragePath; // Directory to store videos.

    @Value("${broker.service.url:http://localhost:8080/broker}")
    private String brokerServiceUrl; // URL for the broker service.

    private final RestTemplate restTemplate;

    // Constructor wiring the RestTemplate.
    public ClientService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Uploads a video, saves it locally, and registers it with the broker service.
     *
     * @param file The video file being uploaded.
     * @return UploadResponse containing metadata of the upload status.
     * @throws IOException if there is an error saving the file.
     */
    @Operation(
            summary = "Upload a video file",
            description = "Uploads a video file, saves it locally, and registers it with the broker service.",
            requestBody = @RequestBody(
                    description = "Video file to upload",
                    required = true,
                    content = @Content(mediaType = "multipart/form-data")
            ),
            responses = {
                    @ApiResponse(responseCode = "200", description = "Video uploaded successfully",
                            content = @Content(schema = @Schema(implementation = UploadResponse.class))),
                    @ApiResponse(responseCode = "400", description = "Invalid input file"),
                    @ApiResponse(responseCode = "500", description = "Error processing the file")
            }
    )
    public UploadResponse uploadVideo(MultipartFile file) throws IOException {
        validateMultipartFile(file);

        // Ensure the video storage directory exists.
        Path uploadDir = Paths.get(videoStoragePath);
        if (!Files.exists(uploadDir)) {
            Files.createDirectories(uploadDir);
        }

        // Generate a unique filename and save the file.
        String uniqueId = UUID.randomUUID().toString();
        String filename = uniqueId + "_" + sanitizeFilename(file.getOriginalFilename());
        Path videoFilePath = uploadDir.resolve(filename);
        file.transferTo(videoFilePath.toFile());

        // Create metadata and register the file with the broker.
        VideoMetadata metadata = new VideoMetadata(uniqueId, filename, "ClientService");
        registerWithBroker(metadata);

        return new UploadResponse(uniqueId, "Video uploaded and registered successfully");
    }

    /**
     * Streams a video with the given video ID.
     *
     * @param videoId The unique ID of the video.
     * @param quality The quality parameter (placeholder for future use).
     * @return ResponseEntity with video data or error status.
     */
    @Operation(
            summary = "Stream a video",
            description = "Streams a video file based on the given unique video ID.",
            responses = {
                    @ApiResponse(responseCode = "200", description = "Video streamed successfully",
                            content = @Content(mediaType = "video/mp4")),
                    @ApiResponse(responseCode = "404", description = "Video not found"),
                    @ApiResponse(responseCode = "500", description = "Error streaming the video")
            }
    )
    public ResponseEntity<byte[]> streamVideo(String videoId, String quality) {
        try {
            // Find the video file by ID.
            Path videoPath = findVideoFileById(videoId)
                    .orElseThrow(() -> new RuntimeException("Video not found: " + videoId));

            // Read the file as a byte array.
            byte[] videoData = Files.readAllBytes(videoPath);

            // Set headers for streaming.
            HttpHeaders headers = new HttpHeaders();
            headers.add(HttpHeaders.CONTENT_TYPE, "video/mp4");
            return ResponseEntity.ok().headers(headers).body(videoData);

        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }

    // ---------------------- Private Helper Methods ---------------------- //

    /**
     * Registers video metadata with the broker service.
     *
     * @param metadata Video metadata to register.
     */
    private void registerWithBroker(VideoMetadata metadata) {
        try {
            restTemplate.postForObject(brokerServiceUrl + "/register", metadata, Void.class);
        } catch (Exception e) {
            throw new RuntimeException("Failed to register video metadata with broker service", e);
        }
    }

    /**
     * Validates that the uploaded MultipartFile is valid.
     *
     * @param file Multipart file to validate.
     * @throws IllegalArgumentException if the file is invalid.
     */
    private void validateMultipartFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("The provided file is empty or null.");
        }
    }

    /**
     * Sanitizes the filename to avoid security vulnerabilities.
     *
     * @param filename The original filename.
     * @return A sanitized filename.
     */
    private String sanitizeFilename(String filename) {
        return Optional.ofNullable(filename)
                .map(name -> name.replaceAll("[^a-zA-Z0-9\\.\\-_]", "_"))
                .orElse("unknown_file");
    }

    /**
     * Finds the path of a video file by its unique ID.
     *
     * @param videoId The unique ID of the video.
     * @return An Optional containing the file path, if found.
     */
    private Optional<Path> findVideoFileById(String videoId) {
        File uploadDir = new File(videoStoragePath);
        if (!uploadDir.exists()) {
            return Optional.empty();
        }

        File[] matchingFiles = uploadDir.listFiles((dir, name) -> name.startsWith(videoId));
        if (matchingFiles == null || matchingFiles.length == 0) {
            return Optional.empty();
        }

        return Optional.of(matchingFiles[0].toPath());
    }

    // ---------------------- OpenAPI Configuration ---------------------- //

    /**
     * Configures the OpenAPI documentation for the Client Service.
     *
     * @return OpenAPI object defining API metadata and configurations.
     */
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Client Service API")
                        .description("This API manages videos for the Client Service, supporting upload and streaming.")
                        .version("1.0")
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0"))
                        .contact(new Contact()
                                .name("Client API Support")
                                .email("support@clientapi.com")
                                .url("https://clientapi-support.com")))

                // Server environments for the API
                .servers(Arrays.asList(
                        new Server().url("http://localhost:8081").description("Local environment"),
                        new Server().url("https://client-service-testing.com").description("Testing server"),
                        new Server().url("https://client-service-live.com").description("Production server")
                ))

                // API Tags for grouping endpoints
                .tags(Arrays.asList(
                        new Tag().name("Video Operations").description("Handles video upload and streaming operations.")
                ))

                // External Documentation link
                .externalDocs(new ExternalDocumentation()
                        .description("Full Client Service API Documentation")
                        .url("https://client-api-full-docs.com"));
    }
}