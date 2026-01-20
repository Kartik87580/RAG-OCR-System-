import React, { useState, useRef } from 'react';
import './UploadPanel.css';

const UploadPanel = ({ onUploadSuccess, userId }) => {
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const uploadedFile = event.target.files[0];
    validateAndSetFile(uploadedFile);
  };

  const validateAndSetFile = (uploadedFile) => {
    if (uploadedFile && uploadedFile.type === 'application/pdf') {
      setFile(uploadedFile);
      setUploadProgress(0);
      setUploadSuccess(false);
    } else {
      alert('Please upload a valid PDF file.');
      setFile(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragOver(false);
    const uploadedFile = event.dataTransfer.files[0];
    validateAndSetFile(uploadedFile);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!file) return;
    if (!userId) {
      alert("You must be logged in to upload.");
      return;
    }

    setUploadProgress(10);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    try {
      // UX Fake Progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) return prev;
          return prev + 10;
        });
      }, 500);

      const response = await fetch('http://localhost:5000/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      clearInterval(progressInterval);

      if (response.ok) {
        setUploadProgress(100);
        setUploadSuccess(true);
        if (onUploadSuccess && data.document_id) {
          onUploadSuccess(data.document_id);
        }
      } else {
        alert(`Upload failed: ${data.detail || 'Unknown error'}`);
        setUploadProgress(0);
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Error uploading file. checking that backend is running.");
      setUploadProgress(0);
    }
  };

  const isProcessing = uploadProgress > 0 && uploadProgress < 100;

  return (
    <div className="upload-card">
      <h2 className="panel-title">Upload Document</h2>

      {!file ? (
        <div
          className={`drag-drop-area ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleBrowseClick}
          style={{ cursor: 'pointer' }}
        >
          <div className="upload-icon-wrapper">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <p className="drag-drop-text">
            Drag & drop PDF here, or <span className="browse-button">Browse</span>
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden-input"
          />
        </div>
      ) : (
        <div className="file-info-card">
          <div className="file-icon">
            <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="file-details">
            <div className="file-name">{file.name}</div>
            <div className="file-status">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </div>
          </div>

          {/* Replace file button */}
          {!isProcessing && !uploadSuccess && (
            <button onClick={() => setFile(null)} style={{ padding: '4px', opacity: 0.6 }}>
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      )}

      {/* Progress & Success States */}
      {file && (
        <div className="status-area">
          {isProcessing && (
            <div className="progress-container">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
              </div>
              <span className="progress-text">{uploadProgress}% Processing...</span>
            </div>
          )}

          {uploadSuccess && (
            <div className="success-state">
              <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Ready to Chat</span>
            </div>
          )}
        </div>
      )}

      <button
        className="process-btn"
        onClick={handleUpload}
        disabled={!file || isProcessing || uploadSuccess}
      >
        {uploadSuccess ? 'Document Processed' : isProcessing ? 'Processing...' : 'Upload & Process'}
      </button>
    </div>
  );
};

export default UploadPanel;