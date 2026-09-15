import React, { createContext, useContext, useState, useEffect } from 'react';
import { sendChatMessage, fetchSessions, fetchSessionMessages } from '../services/api';

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem('lenny_session_id') || null);
  const [llmProvider, setLlmProvider] = useState('local'); // 'local' | 'anthropic' | 'openai' | 'grok'
  const [apiKey, setApiKey] = useState(() => sessionStorage.getItem('lenny_api_key') || '');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState(null); // { type: 'html' | 'markdown' | 'mermaid', content: string, title: string }
  const [sessionsList, setSessionsList] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Load chat history if session exists
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('lenny_session_id', sessionId);
      loadSessionMessages(sessionId);
    } else {
      localStorage.removeItem('lenny_session_id');
      setMessages([]);
    }
  }, [sessionId]);

  // Save API key to sessionStorage
  useEffect(() => {
    if (apiKey) {
      sessionStorage.setItem('lenny_api_key', apiKey);
    } else {
      sessionStorage.removeItem('lenny_api_key');
    }
  }, [apiKey]);

  // Load available sessions on mount
  useEffect(() => {
    loadSessionsList();
  }, []);

  const loadSessionsList = async () => {
    try {
      const data = await fetchSessions();
      setSessionsList(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadSessionMessages = async (id) => {
    setIsLoading(true);
    try {
      const msgs = await fetchSessionMessages(id);
      setMessages(msgs);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewChat = () => {
    setSessionId(null);
    setMessages([]);
    setActiveArtifact(null);
    localStorage.removeItem('lenny_session_id');
    loadSessionsList();
  };

  const loadSpecificSession = (id) => {
    setSessionId(id);
    setActiveArtifact(null);
  };

  const handleProviderSelect = (provider) => {
    if (['anthropic', 'openai', 'grok'].includes(provider)) {
      setLlmProvider(provider);
      setIsModalOpen(true);
    } else {
      setLlmProvider('local');
    }
  };

  const sendMessage = async (content) => {
    if (!content.trim() || isLoading) return;

    if (llmProvider !== 'local' && !apiKey) {
      setIsModalOpen(true);
      return;
    }

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const data = await sendChatMessage({
        sessionId,
        message: content,
        llmProvider,
        apiKey
      });

      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
        loadSessionsList();
      }

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.reply,
        sourceNodes: data.source_nodes || [],
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      detectAndSetArtifact(data.reply);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `⚠️ Failed to get response: ${err.message}. Ensure backend and Ollama/API are running.`,
          sourceNodes: [],
          timestamp: new Date().toISOString(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const detectAndSetArtifact = (text) => {
    const htmlBlock = text.match(/```html([\s\S]*?)```/);
    if (htmlBlock) {
      setActiveArtifact({
        type: 'html',
        content: htmlBlock[1].trim(),
        title: 'Rendered HTML Artifact',
      });
      return;
    }

    const mermaidBlock = text.match(/```mermaid([\s\S]*?)```/);
    if (mermaidBlock) {
      setActiveArtifact({
        type: 'mermaid',
        content: mermaidBlock[1].trim(),
        title: 'Mermaid Diagram',
      });
      return;
    }

    if (text.toLowerCase().includes('# ship 30') || (text.length > 2500 && text.includes('## '))) {
      setActiveArtifact({
        type: 'markdown',
        content: text,
        title: 'Ship 30 for 30 Essay Artifact',
      });
    }
  };

  return (
    <ChatContext.Provider
      value={{
        sessionId,
        llmProvider,
        setLlmProvider: handleProviderSelect,
        apiKey,
        setApiKey,
        isModalOpen,
        setIsModalOpen,
        messages,
        isLoading,
        activeArtifact,
        setActiveArtifact,
        sendMessage,
        startNewChat,
        sessionsList,
        loadSpecificSession
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export const useChat = () => useContext(ChatContext);