import React from 'react';
import { sanitizeHtml } from '../../utils/sanitize';
import './HtmlPreview.css';

export default function HtmlPreview({ content }) {
  const cleanHtml = sanitizeHtml(content);

  // Complete document template injecting Tailwind for high-fidelity component previews.
  // We keep Tailwind via CDN *inside the sandbox only* because the LLM will likely 
  // generate HTML artifacts containing Tailwind classes.
  const bundledSrcDoc = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
          body {
            margin: 0;
            padding: 1.5rem;
            background-color: #0c0a09;
            color: #f5f5f4;
            font-family: ui-sans-serif, system-ui, sans-serif;
          }
        </style>
      </head>
      <body>
        ${cleanHtml}
      </body>
    </html>
  `;

  return (
    <iframe
      title="Artifact HTML Sandbox"
      srcDoc={bundledSrcDoc}
      sandbox="allow-scripts"
      className="html-preview-iframe"
    />
  );
}