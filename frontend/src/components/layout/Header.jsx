import React from 'react';
import { useChat } from '../../context/ChatContext';
import { Cpu, Cloud, Sparkles, Menu } from 'lucide-react';
import './Header.css';

export default function Header({ sidebarOpen, onToggleSidebar }) {
  const { llmProvider, setLlmProvider, logout } = useChat();

  return (
    <header className="header">
      <div className="header-left">
        <button
          type="button"
          onClick={onToggleSidebar}
          aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
          aria-expanded={sidebarOpen}
          className="menu-button"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="logo-icon">
          <Sparkles />
        </div>
        <span className="app-title">
          The Lenny Growth Assistant
        </span>
        <span className="version-badge">
          v1.0
        </span>
      </div>

      <div className="header-right">
        <div className="provider-toggle">
          <button
            type="button"
            onClick={() => setLlmProvider('local')}
            aria-pressed={llmProvider === 'local'}
            className={`provider-button local ${llmProvider === 'local' ? 'active' : ''}`}
          >
            <Cpu className="provider-icon" />
            <span className="provider-text">Local (Ollama)</span>
          </button>
          <button
            type="button"
            onClick={() => setLlmProvider(llmProvider !== 'local' ? llmProvider : 'openai')}
            aria-pressed={llmProvider !== 'local'}
            className={`provider-button cloud ${llmProvider !== 'local' ? 'active' : ''}`}
          >
            <Cloud className="provider-icon" />
            <span className="provider-text">Cloud Provider API</span>
          </button>
        </div>
        <button
          onClick={logout}
          className="logout-button"
          title="Sign out"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}