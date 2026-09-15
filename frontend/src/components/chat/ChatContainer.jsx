import React, { useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import MessageBubble from './MessageBubble';
import { Sparkles } from 'lucide-react';
import './ChatContainer.css';

export default function ChatContainer() {
  const { messages, isLoading } = useChat();
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      // Direct assignment prevents unwanted parent scroll jumping
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="chat-container" ref={containerRef}>
      {messages.length === 0 ? (
        <div className="empty-state">Synthesizing
          <div className="empty-icon-wrapper">
            <Sparkles />
          </div>
          <h2 className="empty-title">The Lenny Growth Assistant</h2>
          <p className="empty-description">
            Directly grounded in Lenny’s Podcast transcripts. Ask product and growth strategy questions, generate Ship 30 essays, or render native UI artifacts beside the chat.
          </p>
        </div>
      ) : (
        <div className="messages-list">
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} />
          ))}
          {isLoading && (
            <div className="loading-indicator">
              <Sparkles />
              <span> Thinking...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}