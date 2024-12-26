import controller.ClientController;
import model.UploadResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;
import service.client.ClientService;

import java.util.UUID;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ClientController.class)
public class ClientServiceTest {

    @MockBean
    private ClientService clientService; // Mocking ClientService

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testUploadVideo() throws Exception {
        // Mock file creation
        MockMultipartFile mockFile = new MockMultipartFile(
                "file",
                "test.mp4",
                MediaType.APPLICATION_OCTET_STREAM_VALUE,
                "dummy content".getBytes()
        );

        // Mock upload response
        String videoId = UUID.randomUUID().toString();
        when(clientService.uploadVideo(mockFile))
                .thenReturn(new UploadResponse(videoId, "Video uploaded and registered successfully"));

        // Perform request and validate response
        mockMvc.perform(multipart("/client/upload").file(mockFile))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.videoId").value(videoId))
                .andExpect(jsonPath("$.message").value("Video uploaded and registered successfully"));
    }

    @Test
    public void testStreamVideo() throws Exception {
        // Mock streaming response
        String videoId = "123";
        String quality = "720p";
        byte[] videoData = "dummy video data".getBytes();
        when(clientService.streamVideo(videoId, quality))
                .thenReturn(org.springframework.http.ResponseEntity.ok()
                        .header(HttpHeaders.CONTENT_TYPE, "video/mp4")
                        .body(videoData));

        // Perform request and validate response
        mockMvc.perform(get("/client/stream/" + videoId).param("quality", quality))
                .andExpect(status().isOk())
                .andExpect(header().string(HttpHeaders.CONTENT_TYPE, "video/mp4"));
    }
}