import React from 'react';
import ReactMarkdown from 'react-markdown';
import './AnswerBox.css';

const AnswerBox = ({
  question = '',
  answer = '',
  sourceChunks = [],
  isUserQuestion = false
}) => {
  return (
    <div className="answer-box-container">

      {/* User Bubble */}
      {isUserQuestion && question && (
        <div className="user-question-bubble">
          <p className="user-question-text">{question}</p>
        </div>
      )}

      {/* AI Bubble */}
      {answer && (
        <div className="ai-answer-card">
          <div className="ai-answer-title">
            AI Assistant
          </div>
          <div className="ai-answer-markdown">
            <ReactMarkdown>{answer}</ReactMarkdown>
          </div>

          {/* Source Chunks */}
          {sourceChunks && sourceChunks.length > 0 && (
            <div className="source-chunks-section">
              <h4 className="source-chunks-title">
                Sources
              </h4>
              <ul className="source-chunks-list">
                {sourceChunks.map((chunk, idx) => (
                  <li
                    key={idx}
                    className="source-chunk-item"
                  >
                    {chunk}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnswerBox;
