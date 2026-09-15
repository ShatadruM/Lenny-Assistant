import React, { useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import MessageBubble from './MessageBubble';
import { Sparkles } from 'lucide-react';
import './ChatContainer.css';

export default function ChatContainer() {
  const { messages, isLoading } = useChat();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-container">
      {messages.length === 0 ? (
        <div className="empty-state">
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
              <span>Synthesizing transcript knowledge...</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}