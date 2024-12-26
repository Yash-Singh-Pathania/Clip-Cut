package controller;

import model.UploadResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import service.client.ClientService;


@RestController
@RequestMapping("/api/client")
public class ClientController {

    private final ClientService clientService;

    public ClientController(ClientService clientService) {
        this.clientService = clientService;
    }

    @PostMapping("/upload")
    public ResponseEntity<UploadResponse> uploadVideo(@RequestParam("file") MultipartFile file) {
        try {
            return ResponseEntity.ok(clientService.uploadVideo(file));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(new UploadResponse(null, e.getMessage()));
        }
    }

    @GetMapping("/stream/{videoId}")
    public ResponseEntity<byte[]> streamVideo(@PathVariable String videoId, @RequestParam(defaultValue = "default") String quality) {
        return clientService.streamVideo(videoId, quality);
    }
}