import React, { useState, useRef } from "react";
import "./DashboardPage.css";

// Mock data for previously uploaded videos
const MOCK_VIDEOS = [
  {
    id: 1,
    title: "First Video",
    thumbnailUrl: "https://via.placeholder.com/120x80?text=First+Vid",
    resolution: "1080p",
    transcriptionLink: "#",
    audioLink: "#",
    editedVideoLink: "#",
  },
  {
    id: 2,
    title: "Second Video",
    thumbnailUrl: "https://via.placeholder.com/120x80?text=Second+Vid",
    resolution: "720p",
    transcriptionLink: "#",
    audioLink: "#",
    editedVideoLink: "#",
  },
  {
    id: 3,
    title: "Third Video",
    thumbnailUrl: "https://via.placeholder.com/120x80?text=Third+Vid",
    resolution: "4K",
    transcriptionLink: "#",
    audioLink: "#",
  },
];

const DashboardPage = () => {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    processFile(file);
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    processFile(file);
  };

  const processFile = (file) => {
    if (!file) return;

    if (file.size > 100 * 1024 * 1024) {
      alert("File size exceeds 100MB. Please upload a smaller file.");
      return;
    }

    if (file.type !== "video/mp4") {
      alert("Only MP4 format is supported.");
      return;
    }

    alert(`File ${file.name} uploaded successfully!`);
  };

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="video-sidebar">
        <h2>Your Videos</h2>
        <div className="video-list">
          {MOCK_VIDEOS.map((video) => (
            <div
              key={video.id}
              className="video-item"
              onClick={() => setSelectedVideo(video)}
            >
              <img
                src={video.thumbnailUrl}
                alt={video.title}
                className="video-thumbnail"
              />
              <div className="video-info">
                <span className="video-title">{video.title}</span>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-dashboard">
        <div
          className="drag-drop-area"
          onClick={handleClick}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="drag-drop-icon">📂</div>
          <div className="drag-drop-text">Drag and drop your video here</div>
          <div className="drag-drop-disclaimer">
            Only MP4 files under 100MB are supported.
          </div>
        </div>

        {/* Hidden input element */}
        <input
          type="file"
          accept="video/mp4"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFileChange}
        />

        {/* Video Details Card */}
        {selectedVideo && (
          <div className="video-details-card">
            <button
              className="close-card-btn"
              onClick={() => setSelectedVideo(null)}
            >
              &times;
            </button>
            <h3>{selectedVideo.title}</h3>
            <p>Resolution: {selectedVideo.resolution}</p>
            <div className="download-links">
              <a href={selectedVideo.editedVideoLink} download>
                Download Edited Video
              </a>
              <a href={selectedVideo.transcriptionLink} download>
                Download Transcription
              </a>
              <a href={selectedVideo.audioLink} download>
                Download Audio
              </a>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardPage;
