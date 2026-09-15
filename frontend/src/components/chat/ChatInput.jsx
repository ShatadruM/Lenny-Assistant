import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { Send, Feather, Loader2 } from 'lucide-react';
import './ChatInput.css';

const MAX_TEXTAREA_HEIGHT = 160; // px

export default function ChatInput() {
  const [input, setInput] = useState('');
  const { sendMessage, isLoading } = useChat();
  const textareaRef = useRef(null);

  // Auto-grow the textarea as the user types, capped at MAX_TEXTAREA_HEIGHT.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  const handleShip30Shortcut = () => {
    if (isLoading) return;
    setInput((prev) => {
      const prefix = 'Write a Ship 30 essay about: ';
      if (prev.startsWith(prefix)) return prev;
      return prefix + prev;
    });
    // Optional: wait a tick for the state to update, then focus the textarea and move cursor to end
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.selectionStart = textareaRef.current.value.length;
        textareaRef.current.selectionEnd = textareaRef.current.value.length;
      }
    }, 0);
  };

  return (
    <div className="chat-input-wrapper">
      <div className="chat-input-inner">
        <div className="shortcuts-row">
          <button
            type="button"
            onClick={handleShip30Shortcut}
            disabled={isLoading}
            className="shortcut-btn"
          >
            <Feather />
            <span>Generate Ship 30 Essay</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="chat-form">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask anything from Lenny's transcripts or generate artifacts..."
            className="chat-textarea"
            style={{ maxHeight: MAX_TEXTAREA_HEIGHT }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            aria-label="Send message"
            className="send-btn"
          >
            {isLoading ? <Loader2 className="spin-icon" /> : <Send />}
          </button>
        </form>
      </div>
    </div>
  );
}