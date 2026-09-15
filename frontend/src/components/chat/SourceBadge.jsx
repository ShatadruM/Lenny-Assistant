import React from 'react';
import { ExternalLink, PlaySquare } from 'lucide-react';
import './SourceBadge.css';

export default function SourceBadge({ source }) {
  if (!source) return null;

  return (
    <a
      href={source.url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="source-badge"
    >
      <PlaySquare className="source-play-icon" />
      <span className="source-title">
        {source.title || 'Lenny Podcast Episode'}
      </span>
      <ExternalLink className="source-link-icon" />
    </a>
  );
}