import React, { useState, useEffect, useRef } from 'react';
import AnswerBox from './AnswerBox';
import './ChatPanel.css';


const ChatPanel = ({ currentDocumentId }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const bottomRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, loading]);

  const handleAsk = async () => {
    if (!question.trim() || loading) return;

    const userQuestion = question;
    setQuestion('');
    setLoading(true);

    try {
      // 🔁 Real RAG API Call
      const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userQuestion,
          document_id: currentDocumentId
        })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      // The backend text response might contain source info or markdown, currently just text
      // We'll trust the answer is in data.answer

      setChatHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          question: userQuestion,
          answer: data.answer,
          sourceChunks: [] // Backend doesn't return structured sources yet
        }
      ]);



    } catch (error) {
      console.error('Error fetching answer:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = () => {
    setChatHistory([]);
    setLoading(false);
  };

  const handleSummary = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: currentDocumentId })
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setChatHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          question: "Document Summary",
          answer: data.answer,
          sourceChunks: []
        }
      ]);
    } catch (error) {
      console.error('Error fetching summary:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-panel-header">
        <h2 className="chat-panel-title">Chat Interface</h2>
        {chatHistory.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="clear-history-button"
          >
            Clear History
          </button>
        )}
        <button
          onClick={handleSummary}
          className="summary-button"
          disabled={loading}
          style={{ marginLeft: '10px', backgroundColor: '#48BB78', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.25rem', cursor: 'pointer' }}
        >
          Summary
        </button>
      </div>

      {/* Chat Area */}
      <div className="chat-history-area custom-scrollbar">
        {chatHistory.length === 0 && !loading && (
          <div className="empty-chat-message">
            Start a conversation by asking a question!
          </div>
        )}

        {chatHistory.map(entry => (
          <AnswerBox
            key={entry.id}
            question={entry.question}
            answer={entry.answer}
            sourceChunks={entry.sourceChunks}
            isUserQuestion={true}
          />
        ))}

        {loading && (
          <div className="loading-spinner-container">
            <div className="loading-spinner"></div>
            <p className="loading-text">Fetching answer...</p>
          </div>
        )}

        <div ref={bottomRef}></div>
      </div>

      {/* Input Area */}
      <div className="question-input-area">
        <textarea
          className="question-textarea"
          placeholder="Ask a question about your documents..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleAsk();
            }
          }}
        />
        <button
          className="ask-button"
          onClick={handleAsk}
          disabled={loading || !question.trim()}
        >
          Ask
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
