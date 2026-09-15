import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MarkdownPreview.css';

export default function MarkdownPreview({ content }) {
  return (
    <div className="markdown-preview-container markdown-preview-prose">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}