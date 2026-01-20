import React, { useState, useEffect, useRef } from 'react';
import AnswerBox from './AnswerBox';
import { supabase } from '../services/supabase';
import './ChatPanel.css';

const ChatPanel = ({ currentDocumentId, userId }) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, loading]);

  // Load History
  useEffect(() => {
    console.log("ChatPanel: useEffect triggered", { currentDocumentId, userId });
    if (currentDocumentId && userId) {
      setLoading(true);
      const fetchHistory = async () => {
        console.log(`Fetching history for doc: ${currentDocumentId}, user: ${userId}`);
        const { data, error } = await supabase
          .from('chats')
          .select('*')
          .eq('document_id', currentDocumentId)
          .eq('user_id', userId)
          .order('created_at', { ascending: true });

        if (error) {
          console.error("Error fetching history:", error);
        } else if (data) {
          console.log("History fetched:", data.length, "records");
          const history = data.map(item => ({
            id: item.id,
            question: item.question,
            answer: item.answer,
            sourceChunks: [] // History doesn't have chunks yet unless we store them.
          }));
          setChatHistory(history);
        }
        setLoading(false);
      };
      fetchHistory();
    } else {
      setChatHistory([]);
    }
  }, [currentDocumentId, userId]);

  const handleAsk = async () => {
    if (!question.trim() || loading) return;

    const userQuestion = question;
    setQuestion('');
    setLoading(true);

    // Reset height of textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = '50px';
    }

    try {
      const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userQuestion,
          document_id: currentDocumentId,
          user_id: userId
        })
      });

      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();

      setChatHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          question: userQuestion,
          answer: data.answer,
          sourceChunks: []
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
        body: JSON.stringify({
          document_id: currentDocumentId,
          user_id: userId
        })
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setChatHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          question: "Generate Summary",
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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-panel-header">
        <h2 className="chat-panel-title">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          Chat Session
        </h2>

        <div className="header-actions">
          {/* Mode Toggle (Visual Only as backend is same) */}
          <div className="mode-toggle">
            <button className="toggle-btn active">Chat</button>
            <button
              className="toggle-btn"
              onClick={handleSummary}
              disabled={loading}
            >
              Summary
            </button>
          </div>


        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-history-area custom-scrollbar">
        {chatHistory.length === 0 && !loading && (
          <div className="empty-chat-message">
            <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="var(--border-light)">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p>Ask a question about your documents to get started.</p>
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
          <div className="loading-indicator">
            <div className="spinner"></div>
            <span>Thinking...</span>
          </div>
        )}

        <div ref={bottomRef}></div>
      </div>

      {/* Input Area */}
      <div className="question-input-area">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            className="question-textarea"
            placeholder="Type your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="send-btn"
            onClick={handleAsk}
            disabled={loading || !question.trim()}
          >
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
