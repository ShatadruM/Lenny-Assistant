import React from 'react';
import { useChat } from '../../context/ChatContext';
import { Plus, MessageSquare, Database, Terminal, X } from 'lucide-react';
import './Sidebar.css';

export default function Sidebar({ open, onClose }) {
  const { sessionId, startNewChat, sessionsList, loadSpecificSession } = useChat();

  const handleNewChat = () => {
    startNewChat();
    onClose?.();
  };

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="sidebar-backdrop"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside className={`sidebar ${open ? 'open' : 'closed'}`}>
        <div className="sidebar-top">
          <div className="sidebar-mobile-header">
            <span className="sidebar-menu-label">Menu</span>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close sidebar"
              className="sidebar-close-btn"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <button
            type="button"
            onClick={handleNewChat}
            className="new-session-btn"
          >
            <Plus className="w-4 h-4" />
            <span>New Growth Session</span>
          </button>

          <div className="current-session-container">
            <p className="session-label">Current Session</p>
            <div className="session-info">
              <MessageSquare className="w-3.5 h-3.5" />
              <span className="session-id">
                {sessionId ? `${sessionId.slice(0, 16)}...` : 'Unsaved / New Session'}
              </span>
            </div>
          </div>

          <div className="history-container">
            <p className="session-label">History</p>
            {sessionsList.map(session => (
              <button 
                key={session.id} 
                className={`history-item ${session.id === sessionId ? 'active' : ''}`}
                onClick={() => {
                  loadSpecificSession(session.id);
                  onClose?.();
                }}
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span className="history-title">Session {session.id.slice(0,6)}</span>
                <span className="history-date">
                  {new Date(session.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="status-item">
            <Database className="w-3.5 h-3.5 emerald-icon" />
            <span>Supabase pgvector</span>
          </div>
          <div className="status-item">
            <Terminal className="w-3.5 h-3.5 orange-icon" />
            <span>RTX 4050 Active</span>
          </div>
        </div>
      </aside>
    </>
  );
}