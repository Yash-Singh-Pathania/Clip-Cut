import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./DashboardPage.css";

const DashboardPage = ({ user }) => {
  const [modal, setModal] = useState({
    open: false,
    message: "",
    onOk: null,
    type: "info",
  });

  const [processedVideos, setProcessedVideos] = useState([]);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const wsUrl = "ws://localhost:8002/ws";
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("WebSocket connected to monitoring service");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === "video_processed") {
          console.log("Got video_processed event:", data);
          setProcessedVideos((prev) => [...prev, data]);
        }
      } catch (error) {
        console.error("Failed to parse WS message", error);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const closeModal = () => {
    setModal({ ...modal, open: false, message: "", onOk: null });
  };

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
      setModal({
        open: true,
        message: "File size exceeds 100MB. Please upload a smaller file.",
        onOk: closeModal,
        type: "error",
      });
      return;
    }

    if (file.type !== "video/mp4") {
      setModal({
        open: true,
        message: "Only MP4 format is supported.",
        onOk: closeModal,
        type: "error",
      });
      return;
    }

    try {
      const userId = user?.userId || "unknown"; 
      const url = `${process.env.REACT_APP_VIDEO_UPLOAD_SERVICE_URL}/upload-video/?user_id=${encodeURIComponent(
        userId
      )}`;

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        setModal({
          open: true,
          message: `Error: ${errData.detail || "Unable to upload video"}`,
          onOk: closeModal,
          type: "error",
        });
      } else {
        const data = await response.json();
        setModal({
          open: true,
          message: `File ${file.name} uploaded successfully! Video ID: ${data.video_id}. Please wait...`,
          onOk: closeModal,
          type: "info",
        });
      }
    } catch (error) {
      setModal({
        open: true,
        message: "An error occurred while uploading the video.",
        onOk: closeModal,
        type: "error",
      });
    }
  };

  return (
    <div className="dashboard-container">
      <aside className="video-sidebar">
        <h2>Your Videos</h2>
        <div className="user-info">
          <div className="user-icon">👤</div>
          <div className="user-name">
            {user?.name || "Guest User"}
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

        {/* Display any processed videos */}
        <div className="processed-list">
          {processedVideos.map((item, idx) => {
            /*
              item structure (from monitoring service) might be:
              {
                event: "video_processed",
                video_id: "...",
                file_name: "...",
                transcript_file_id: "...",
                resolutions: { "720p": "ID720", ... },
                download_links: { "720p": "http://localhost:8002/download/ID720", ... },
                download_transcript: "http://localhost:8002/download/IDTXT"
                message: "Video fully processed. Ready to download."
              }
            */
            return (
              <div key={idx} className="processed-item">
                <h3>Video ID: {item.video_id}</h3>

                {/* If "download_links" is present, use it directly */}
                {item.download_links ? (
                  <div className="download-links">
                    {Object.entries(item.download_links).map(([res, link]) => (
                      <div key={res}>
                        <a href={link} download>
                          Download {res}
                        </a>
                      </div>
                    ))}
                  </div>
                ) : (
                  // fallback if the service didn't embed links
                  <div className="download-links">
                    {Object.entries(item.resolutions || {}).map(([res, fileId]) => {
                      if (!fileId) return null;
                      const fallbackUrl = `http://localhost:8002/download/${fileId}`;
                      return (
                        <div key={res}>
                          <a href={fallbackUrl} download>
                            Download {res}
                          </a>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* If we have a separate "download_transcript" link */}
                {item.download_transcript ? (
                  <div className="transcript-download">
                    <a href={item.download_transcript} download>
                      Download Transcript
                    </a>
                  </div>
                ) : item.transcript_file_id ? (
                  // fallback if only transcript_file_id is present
                  <div className="transcript-download">
                    <a
                      href={`http://localhost:8002/download/${item.transcript_file_id}`}
                      download
                    >
                      Download Transcript
                    </a>
                  </div>
                ) : (
                  <p>No transcript available</p>
                )}
              </div>
            );
          })}
        </div>
      </main>

      {modal.open && (
        <div className="modal-overlay">
          <div className="modal-content">
            <p>{modal.message}</p>
            <div className="modal-buttons">
              <button onClick={modal.onOk}>OK</button>
              {modal.type !== "info" && (
                <button onClick={closeModal}>Close</button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
