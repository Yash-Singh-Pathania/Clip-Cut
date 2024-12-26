package model;

public class VideoMetadata {
    private String fileName;
    private String clientName;

    public VideoMetadata(String videoId, String fileName, String clientName) {
        this.fileName = fileName;
        this.clientName = clientName;
    }

    // Getter and Setter methods omitted for brevity
}