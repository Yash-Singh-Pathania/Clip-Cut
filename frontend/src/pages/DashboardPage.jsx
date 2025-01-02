import React, { useState, useRef } from "react";
import "./DashboardPage.css";

const DashboardPage = ({ user }) => {
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

  const processFile = async (file) => {
    if (!file) return;

    if (file.size > 100 * 1024 * 1024) {
      alert("File size exceeds 100MB. Please upload a smaller file.");
      return;
    }

    if (file.type !== "video/mp4") {
      alert("Only MP4 format is supported.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("user_id", user?.userId || "unknown"); // Fallback for user ID
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8001/upload-video/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        alert(`Error: ${errData.detail || "Unable to upload video"}`);
      } else {
        const data = await response.json();
        alert(`File ${file.name} uploaded successfully! Video ID: ${data.video_id}`);
      }
    } catch (error) {
      alert("An error occurred while uploading the video.");
    }
  };

  return (
    <div className="dashboard-container">
      <aside className="video-sidebar">
        <h2>Your Videos</h2>

        {/* User Info Section */}
        <div className="user-info">
          <div className="user-icon">👤</div>
          <div className="user-name">
            {user?.name || "Guest User"} {/* Fallback for user name */}
          </div>
        </div>
      </aside>

      <main className="main-dashboard">
        <div
          className="drag-drop-area"
          onClick={handleClick}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="drag-drop-icon">📂</div>
          <div className="drag-drop-text">Drag and drop your video here</div>
        </div>

        <input
          type="file"
          accept="video/mp4"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFileChange}
        />
      </main>
    </div>
  );
};

export default DashboardPage;
