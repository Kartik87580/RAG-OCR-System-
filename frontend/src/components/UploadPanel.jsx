import React, { useState } from 'react';
import './UploadPanel.css';

const UploadPanel = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileChange = (event) => {
    const uploadedFile = event.target.files[0];
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
    if (uploadedFile && uploadedFile.type === 'application/pdf') {
      setFile(uploadedFile);
      setUploadProgress(0);
      setUploadSuccess(false);
    } else {
      alert('Please drop a valid PDF file.');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a PDF file to upload.');
      return;
    }

    setUploadProgress(10);
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Start fake progress for better UX before request completes
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

  return (
    <div className="pdf-upload-panel">
      <h2 className="panel-title">Upload Your PDF Document</h2>

      <div
        className={`drag-drop-area ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <p className="drag-drop-text">Drag & drop your PDF here, or</p>
        <label
          htmlFor="pdf-upload"
          className="browse-button"
        >
          Browse Files
        </label>
        <input
          id="pdf-upload"
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden-input"
        />
        {file && <p className="selected-file-name">Selected: {file.name}</p>}
      </div>

      {file && !uploadSuccess && (
        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${uploadProgress}%` }}
          ></div>
          <span className="progress-text">
            {uploadProgress}%
          </span>
        </div>
      )}

      {uploadSuccess && (
        <div className="success-message">
          <svg
            className="success-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          PDF Uploaded Successfully!
        </div>
      )}

      <button
        className="process-document-button"
        onClick={handleUpload}
        disabled={!file || (uploadProgress > 0 && uploadProgress < 100)}
      >
        Process Document
      </button>
    </div>
  );
};

export default UploadPanel;