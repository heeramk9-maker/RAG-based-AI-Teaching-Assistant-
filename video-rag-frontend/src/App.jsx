"use client"

import { useState, useEffect } from "react"
import "./App.css"

export default function App() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [videos, setVideos] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadLoading, setUploadLoading] = useState(false)

  useEffect(() => {
    fetchAllVideos()
  }, [])

  const fetchAllVideos = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/videos")
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()

      // Transform the video filenames into the format expected by the UI
      const videoList = data.videos.map((filename) => ({
        id: filename,
        name: filename,
        size: "Unknown", // Size info not available from the API
      }))

      setVideos(videoList)
      console.log("[v0] Fetched videos:", videoList)
    } catch (err) {
      console.error("Error fetching videos:", err)
      setError("Failed to fetch video list from server")
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    setError("")
    setAnswer("")

    try {
      const response = await fetch("http://127.0.0.1:5000/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setAnswer(data.answer || "No answer received")
    } catch (err) {
      console.error("Error:", err)
      setError("Failed to get answer. Please make sure your Flask server is running on http://127.0.0.1:5000")
    } finally {
      setLoading(false)
    }
  }

  const handleVideoUpload = async (e) => {
    e.preventDefault()
    if (!selectedFile) return

    setUploadLoading(true)
    setError("")

    try {
      const formData = new FormData()
      formData.append("file", selectedFile)

      const response = await fetch("http://127.0.0.1:5000/api/upload_video", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Refresh the entire video list from server to ensure consistency
      await fetchAllVideos()

      setSelectedFile(null)
      setSidebarOpen(false)
    } catch (err) {
      console.error("Error:", err)
      setError("Failed to upload video. Please make sure your Flask server is running.")
    } finally {
      setUploadLoading(false)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      const allowedTypes = ["video/mp4", "video/mov", "video/avi", "video/x-msvideo"]
      if (allowedTypes.includes(file.type) || file.name.toLowerCase().endsWith(".mkv")) {
        setSelectedFile(file)
        setError("")
      } else {
        setError("Please select a valid video file (MP4, MOV, AVI, MKV)")
        setSelectedFile(null)
      }
    }
  }

  const deleteVideo = async (videoId, e) => {
    e.stopPropagation() // Prevent any unwanted clicks

    if (!confirm(`Are you sure you want to delete "${videoId}"?`)) {
      return
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/videos/${videoId}`, {
        method: "DELETE",
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Refresh the video list
      await fetchAllVideos()
    } catch (err) {
      console.error("Error deleting video:", err)
      setError("Failed to delete video. Please try again.")
    }
  }

  return (
    <div className="app">
      <button className="hamburger-button" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle menu">
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
      </button>

      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          style={{ display: window.innerWidth <= 640 ? "block" : "none" }}
        ></div>
      )}

      <div className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-header">
          <h3>Video Library</h3>
          <button className="close-button" onClick={() => setSidebarOpen(false)}>
            ×
          </button>
        </div>

        <div className="upload-section">
          <h4>Upload New Video</h4>
          <form onSubmit={handleVideoUpload} className="upload-form">
            <div className="file-input-wrapper">
              <input
                type="file"
                accept="video/mp4,video/mov,video/avi,video/x-msvideo,.mkv"
                onChange={handleFileSelect}
                className="file-input"
                id="video-file"
                disabled={uploadLoading}
              />
              <label htmlFor="video-file" className="file-input-label">
                {selectedFile ? selectedFile.name : "Choose video file..."}
              </label>
            </div>
            {selectedFile && (
              <div className="file-info">
                <span>Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
              </div>
            )}
            <button type="submit" disabled={uploadLoading || !selectedFile} className="upload-button">
              {uploadLoading ? "Uploading..." : "Upload Video"}
            </button>
          </form>
        </div>

        {/* Videos List */}
        <div className="videos-section">
          <h4>Uploaded Videos ({videos.length})</h4>
          {videos.length === 0 ? (
            <p className="no-videos">No videos uploaded yet</p>
          ) : (
            <div className="videos-list">
              {videos.map((video) => (
                <div
                  key={video.id}
                  className="video-item" // Removed selection styling and click handler
                >
                  <div className="video-info">
                    <span className="video-name">{video.name}</span>
                    <span className="video-size">{video.size}</span>
                  </div>
                  <div className="video-actions">
                    <button
                      className="delete-button"
                      onClick={(e) => deleteVideo(video.id, e)}
                      title={`Delete ${video.name}`}
                      aria-label={`Delete ${video.name}`}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="container">
        {/* Header */}
        <div className="header">
          <div className="header-content">
            <div className="brain-icon">🧠</div>
            <div>
              <h1 className="title">Video RAG AI</h1>
              <p className="subtitle">Ask questions about your uploaded videos</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="main-content">
          {/* Question Form */}
          <div className="question-card">
            <div className="card-header">
              <span className="message-icon">💬</span>
              <h2>Ask a Question</h2>
            </div>
            <form onSubmit={handleSubmit} className="question-form">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What would you like to know about your videos?" // Simplified placeholder
                className="question-input"
                rows={4}
                disabled={loading} // Only disabled during loading
              />
              <button
                type="submit"
                disabled={loading || !question.trim()} // Removed video selection requirement
                className="submit-button"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Processing...
                  </>
                ) : (
                  "Ask Question"
                )}
              </button>
            </form>
          </div>

          {/* Answer Display */}
          {(answer || error) && (
            <div className="answer-card">
              <div className="card-header">
                <span className="answer-icon">🤖</span>
                <h2>AI Response</h2>
              </div>
              {error ? (
                <div className="error-message">
                  <span className="error-icon">⚠️</span>
                  {error}
                </div>
              ) : (
                <div className="answer-content">{answer}</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
