import React from 'react';
import './AnswerBox.css';

const AnswerBox = ({
  question = '',
  answer = '',
  sourceChunks = [],
  isUserQuestion = false
}) => {
  return (
    <div className="answer-box-container">
      
      {/* User Question */}
      {isUserQuestion && question && (
        <div className="user-question-bubble">
          <p className="user-question-label">You asked:</p>
          <p className="user-question-text">{question}</p>
        </div>
      )}

      {/* AI Answer */}
      <div className="ai-answer-card">
        <h3 className="ai-answer-title">AI-Generated Answer</h3>
        <p className="ai-answer-text">{answer}</p>

        {/* Source Chunks */}
        {sourceChunks.length > 0 && (
          <div className="source-chunks-section">
            <h4 className="source-chunks-title">
              Source Document Chunks
            </h4>
            <ul className="source-chunks-list">
              {sourceChunks.map((chunk) => (
                <li
                  key={`${chunk}-${Math.random()}`}
                  className="source-chunk-item"
                >
                  {chunk}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

    </div>
  );
};

export default AnswerBox;
