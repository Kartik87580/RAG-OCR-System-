import React, { useState } from 'react';
import UploadPanel from './components/UploadPanel';
import ChatPanel from './components/ChatPanel';
import './App.css';

function App() {
  const [currentDocumentId, setCurrentDocumentId] = useState(null);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1 className="app-title">Chat with Your Documents</h1>
        <p className="app-subtitle">
          Upload PDFs and ask questions using AI-powered retrieval
        </p>
      </header>

      {/* Main Layout */}
      <div className="content-wrapper">
        {/* LEFT */}
        <aside className="left-panel">
          <UploadPanel onUploadSuccess={setCurrentDocumentId} />
        </aside>

        {/* RIGHT */}
        <main className="right-panel">
          <ChatPanel currentDocumentId={currentDocumentId} />
        </main>
      </div>
    </div>
  );
}

export default App;
