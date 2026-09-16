import React, { useState, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { X } from 'lucide-react';
import './ApiKeyModal.css';

export default function ApiKeyModal() {
  const { isModalOpen, setIsModalOpen, llmProvider, setLlmProvider, apiKey, setApiKey } = useChat();
  const [localProvider, setLocalProvider] = useState(llmProvider === 'local' ? 'openai' : llmProvider);
  const [localKey, setLocalKey] = useState('');

  useEffect(() => {
    if (isModalOpen) {
      setLocalProvider(llmProvider === 'local' ? 'openai' : llmProvider);
      setLocalKey(apiKey);
    }
  }, [isModalOpen, llmProvider, apiKey]);

  if (!isModalOpen) return null;

  const handleSave = () => {
    setLlmProvider(localProvider);
    setApiKey(localKey);
    setIsModalOpen(false);
  };

  const handleClose = () => {
    if (llmProvider !== 'local' && llmProvider !== 'groq' && !apiKey) {
      // Revert to local if they cancel without saving a key (unless Groq is allowed to be empty)
      setLlmProvider('local');
    }
    setIsModalOpen(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h3 className="modal-title">Cloud AI Provider Settings</h3>
          <button type="button" onClick={handleClose} className="modal-close-btn">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="modal-body">
          <div className="provider-select-group">
            <label className="provider-select-label">Select Provider</label>
            <select
              value={localProvider}
              onChange={(e) => setLocalProvider(e.target.value)}
              className="provider-select"
            >
              <option value="openai">OpenAI (GPT-4o)</option>
              <option value="anthropic">Anthropic (Claude 3.5)</option>
              <option value="groq">Groq (Llama 3.1 70B)</option>
            </select>
          </div>

          <div className="api-key-group">
            <label className="provider-select-label">API Key</label>
            <input
              type="password"
              value={localKey}
              onChange={(e) => setLocalKey(e.target.value)}
              placeholder={`Enter your ${localProvider} API key...`}
              className="api-key-input"
            />
            {localProvider === 'groq' && (
              <button 
                type="button" 
                onClick={() => {
                  setLocalKey('');
                  handleSave(); // Auto-save and close when they click this
                }}
                className="btn-save"
                style={{ marginTop: '10px', width: '100%', backgroundColor: '#10b981' }}
              >
                Use Pre-provided Groq LLM
              </button>
            )}
            <span className="api-key-hint">
              Your key is only stored in your browser's current session and sent directly to the backend. It clears when you close the tab.
            </span>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" onClick={handleClose} className="btn-cancel">
            Cancel
          </button>
          <button type="button" onClick={handleSave} className="btn-save">
            Save and Continue
          </button>
        </div>
      </div>
    </div>
  );
}
