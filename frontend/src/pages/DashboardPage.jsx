import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./DashboardPage.css";

const DashboardPage = ({ user }) => {
  const mimicOnLoad = false;
  const [modal, setModal] = useState({
    open: false,
    message: "",
    onOk: null,
    type: "info",
  });
  const [processedVideos, setProcessedVideos] = useState([]);
  const [downloadAlert, setDownloadAlert] = useState({ show: false, message: "" });
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const wsUrl = "ws://localhost:8082/ws";
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

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  // Mimic logic only if mimicOnLoad === true (currently false)
  useEffect(() => {
    if (mimicOnLoad) {
      const timer = setTimeout(() => {
        const fakeData = {
          event: "video_processed",
          video_id: "test",
          message: "Video processed (onLoad = true). Ready to download!",
          resolutions: {
            "720p": "1_test_720p.mp4",
            "480p": "1_test_480p.mp4",
          },
          transcript_file_id: "1_test_transcript.txt",
          download_links: {
            "720p": "/1_test_720p.mp4",
            "480p": "/1_test_480p.mp4",
          },
          download_transcript_txt: "/1_test_transcription.txt",
          download_transcript_srt: "/1_test_transcription.srt",
        };
        setProcessedVideos((prev) => [...prev, fakeData]);
      }, 7000);

      return () => clearTimeout(timer);
    }
  }, [mimicOnLoad]);

  const closeModal = () => {
    setModal((prev) => ({ ...prev, open: false, message: "", onOk: null }));
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

      const response = await fetch(url, { method: "POST", body: formData });

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

        if (!mimicOnLoad) {
          // mimic event 30s after upload
          setTimeout(() => {
            const fakeData = {
              event: "video_processed",
              video_id: "test",
              message: "Video processed (onLoad = false). Ready to download!",
              resolutions: {
                "720p": "1_test_720p.mp4",
                "480p": "1_test_480p.mp4",
              },
              transcript_file_id: "1_test_transcription.txt",
              download_links: {
                "720p": "/1_test_720p.mp4",
                "480p": "/1_test_480p.mp4",
              },
              download_transcript_txt: "/1_test_transcription.txt",
              download_transcript_srt: "/1_test_transcription.srt",
            };
            setProcessedVideos((prev) => [...prev, fakeData]);
          }, 30000);
        }
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

  // Simple logout handler
  const handleLogout = () => {
    // Clear any session or tokens here, if needed
    navigate("/login");
  };

  // Show a quick popup when downloading
  const handleDownloadClick = (e, link) => {
    e.preventDefault();
    setDownloadAlert({ show: true, message: "Starting download..." });

    setTimeout(() => {
      setDownloadAlert({ show: false, message: "" });
      const anchor = document.createElement("a");
      anchor.href = link;
      anchor.download = ""; // triggers download w/ default filename
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
    }, 1200);
  };

  return (
    <div className="dashboard-container">
      <main className="main-dashboard">
        <div
          className="drag-drop-area"
          onClick={handleClick}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="drag-drop-icon">📂</div>
          <div className="drag-drop-text">Drag and drop your video here to get transcripts and 
          different resolution</div>
        </div>

        <input
          type="file"
          accept="video/mp4"
          ref={fileInputRef}
          onChange={handleFileChange}
        />
      </main>

      <aside className="video-sidebar">
        <div className="user-info">
          <div className="user-icon">👤</div>
          <div className="user-name">{user?.name || "Guest User"}</div>
        </div>

        <h2>Your Videos</h2>
        <div className="processed-list">
          {processedVideos.map((item, idx) => (
            <div key={idx} className="processed-item">
              <h3>Video ID: {item.video_id}</h3>
              <p className="processed-message">{item.message}</p>
              {item.download_links ? (
                <div className="download-links">
                  {Object.entries(item.download_links).map(([res, link]) => (
                    <button
                      key={res}
                      className="download-button"
                      onClick={(e) => handleDownloadClick(e, link)}
                    >
                      Download {res}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="download-links">
                  {Object.entries(item.resolutions || {}).map(([res, fileId]) => {
                    if (!fileId) return null;
                    const fallbackUrl = `http://localhost:8002/download/${fileId}`;
                    return (
                      <button
                        key={res}
                        className="download-button"
                        onClick={(e) => handleDownloadClick(e, fallbackUrl)}
                      >
                        Download {res}
                      </button>
                    );
                  })}
                </div>
              )}

              <div className="transcript-download">
                {item.download_transcript_txt && (
                  <button
                    className="download-button"
                    onClick={(e) => handleDownloadClick(e, item.download_transcript_txt)}
                  >
                    Download Transcript (TXT)
                  </button>
                )}
                {item.download_transcript_srt && (
                  <button
                    className="download-button"
                    onClick={(e) => handleDownloadClick(e, item.download_transcript_srt)}
                  >
                    Download Transcript (SRT)
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Logout button placed at the bottom of sidebar */}
        <div className="logout-container">
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>

      {/* Modal logic */}
      {modal.open && (
        <div className="modal-overlay">
          <div className="modal-content">
            <p>{modal.message}</p>
            <div className="modal-buttons">
              <button onClick={modal.onOk}>OK</button>
              {modal.type !== "info" && <button onClick={closeModal}>Close</button>}
            </div>
          </div>
        </div>
      )}

      {/* Download alert popup */}
      {downloadAlert.show && (
        <div className="download-popup">
          <p>{downloadAlert.message}</p>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
