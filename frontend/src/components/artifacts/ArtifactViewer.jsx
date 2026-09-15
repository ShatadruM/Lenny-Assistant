import React, { useState, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import HtmlPreview from './HtmlPreview';
import MarkdownPreview from './MarkdownPreview';
import MermaidPreview from './MermaidPreview';
import { X, Code, Eye, Copy, Check } from 'lucide-react';
import './ArtifactViewer.css';

export default function ArtifactViewer() {
  const { activeArtifact, setActiveArtifact } = useChat();
  const [viewMode, setViewMode] = useState('preview'); // 'preview' | 'code'
  const [copied, setCopied] = useState(false);

  // Reset back to preview whenever a new artifact is opened.
  useEffect(() => {
    if (activeArtifact) setViewMode('preview');
  }, [activeArtifact]);

  // Guard against the "Copied" state leaking into a later render / unmount.
  useEffect(() => {
    if (!copied) return;
    const timer = setTimeout(() => setCopied(false), 2000);
    return () => clearTimeout(timer);
  }, [copied]);

  if (!activeArtifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(activeArtifact.content);
    setCopied(true);
  };

  return (
    <aside className="artifact-viewer">
      <header className="artifact-header">
        <div className="artifact-header-left">
          <span className="artifact-title">{activeArtifact.title}</span>
          <span className="artifact-badge">
            {activeArtifact.type.toUpperCase()}
          </span>
        </div>

        <div className="artifact-header-right">
          <div className="view-mode-toggle">
            <button
              type="button"
              onClick={() => setViewMode('preview')}
              aria-pressed={viewMode === 'preview'}
              className={`view-mode-btn ${viewMode === 'preview' ? 'active' : ''}`}
            >
              <Eye />
              <span className="btn-text">Preview</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('code')}
              aria-pressed={viewMode === 'code'}
              className={`view-mode-btn ${viewMode === 'code' ? 'active' : ''}`}
            >
              <Code />
              <span className="btn-text">Code</span>
            </button>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            aria-label="Copy artifact content"
            className="icon-btn"
          >
            {copied ? <Check className="check-icon" /> : <Copy />}
          </button>

          <button
            type="button"
            onClick={() => setActiveArtifact(null)}
            aria-label="Close artifact viewer"
            className="icon-btn"
          >
            <X />
          </button>
        </div>
      </header>

      <div className="artifact-content-area">
        {viewMode === 'code' ? (
          <pre className="code-preview">
            {activeArtifact.content}
          </pre>
        ) : activeArtifact.type === 'html' ? (
          <HtmlPreview content={activeArtifact.content} />
        ) : activeArtifact.type === 'mermaid' ? (
          <MermaidPreview content={activeArtifact.content} />
        ) : (
          <MarkdownPreview content={activeArtifact.content} />
        )}
      </div>
    </aside>
  );
}