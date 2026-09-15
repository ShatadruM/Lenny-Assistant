import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import './MermaidPreview.css';

// Configure mermaid for a dark theme matching our UI
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#f97316',
    primaryTextColor: '#f5f5f4',
    primaryBorderColor: '#fb923c',
    lineColor: '#f5f5f4',
    secondaryColor: '#44403c',
    tertiaryColor: '#292524'
  },
  fontFamily: 'ui-sans-serif, system-ui, sans-serif'
});

export default function MermaidPreview({ content }) {
  const containerRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    
    const renderDiagram = async () => {
      try {
        setError(null);
        if (containerRef.current) {
          // Clear previous render
          containerRef.current.innerHTML = '';
          const id = `mermaid-${Date.now()}`;
          const { svg } = await mermaid.render(id, content);
          
          if (isMounted && containerRef.current) {
            containerRef.current.innerHTML = svg;
          }
        }
      } catch (err) {
        console.error("Mermaid parsing error:", err);
        if (isMounted) {
          setError(err.message || 'Failed to parse Mermaid code. The AI might have generated invalid syntax.');
        }
      }
    };

    renderDiagram();

    return () => {
      isMounted = false;
    };
  }, [content]);

  return (
    <div className="mermaid-preview-container">
      {error ? (
        <div className="mermaid-error" style={{ color: '#ef4444', padding: '1rem', border: '1px solid #7f1d1d', borderRadius: '0.5rem', backgroundColor: '#450a0a' }}>
          <strong>Diagram Error:</strong> <br />
          {error}
        </div>
      ) : (
        <div className="mermaid-content" ref={containerRef}>
          {/* SVG will be injected here */}
        </div>
      )}
    </div>
  );
}
