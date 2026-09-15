import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SourceBadge from './SourceBadge';
import { useChat } from '../../context/ChatContext';
import { LayoutDashboard, FileText, User, Sparkles } from 'lucide-react';
import './MessageBubble.css';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const { setActiveArtifact } = useChat();

  const containsHtml = message.content.includes('```html');
  const containsShip30 = message.content.includes('# Ship 30');
  const isArtifact = containsHtml || containsShip30;

  const handleOpenArtifact = () => {
    if (containsHtml) {
      const match = message.content.match(/```html([\s\S]*?)```/);
      setActiveArtifact({
        type: 'html',
        content: match ? match[1].trim() : '',
        title: 'Rendered HTML Artifact',
      });
    } else {
      setActiveArtifact({
        type: 'markdown',
        content: message.content,
        title: 'Ship 30 for 30 Essay Artifact',
      });
    }
  };

  return (
    <div className={`message-bubble-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className={`message-bubble-inner ${isUser ? 'user' : 'assistant'}`}>
        <div className={`message-avatar ${isUser ? 'user' : 'assistant'}`}>
          {isUser ? <User /> : <Sparkles />}
        </div>

        <div className="message-content-wrapper">
          <div className={`message-body markdown-prose ${isUser ? 'user' : 'assistant'}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>

          {isArtifact && !isUser && (
            <button
              type="button"
              onClick={handleOpenArtifact}
              className="open-artifact-btn"
            >
              {containsHtml ? <LayoutDashboard /> : <FileText />}
              <span>Open in Artifact Viewer</span>
            </button>
          )}

          {message.sourceNodes && message.sourceNodes.length > 0 && (
            <div className="sources-container">
              <span className="sources-label">
                Grounded Knowledge Sources
              </span>
              <div className="sources-list">
                {message.sourceNodes.map((src, i) => (
                  <SourceBadge key={src?.url ?? src?.title ?? i} source={src} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}