import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchSessionMessages } from '../services/api';

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('oogway_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [sessionId, setSessionId] = useState(() => localStorage.getItem('oogway_session_id') || null);
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
      localStorage.setItem('oogway_session_id', sessionId);
      loadSessionMessages(sessionId);
    } else {
      localStorage.removeItem('oogway_session_id');
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

  // Load available sessions on mount / user change
  useEffect(() => {
    if (user) {
      localStorage.setItem('oogway_user', JSON.stringify(user));
      loadSessionsList();
    } else {
      localStorage.removeItem('oogway_user');
      setSessionsList([]);
      setSessionId(null);
      setMessages([]);
    }
  }, [user]);

  const loadSessionsList = async () => {
    if (!user) return;
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/sessions?user_id=${user.user_id}`);
      const data = await res.json();
      setSessionsList(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadSessionMessages = async (sid) => {
    setIsLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/sessions/${sid}/messages`);
      const data = await res.json();
      setMessages(data);
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
    localStorage.removeItem('oogway_session_id');
    loadSessionsList();
  };

  const loadSpecificSession = (id) => {
    setSessionId(id);
    setActiveArtifact(null);
  };

  const handleProviderSelect = (provider) => {
    if (['anthropic', 'openai', 'groq'].includes(provider)) {
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
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: user?.user_id,
          message: content,
          llm_provider: llmProvider,
          api_key: apiKey
        }),
      });

      const data = await res.json();

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

  const logout = () => {
    setUser(null);
  };

  return (
    <ChatContext.Provider
      value={{
        user,
        setUser,
        logout,
        sessionId,
        llmProvider,
        setLlmProvider: handleProviderSelect,
        handleProviderSelect,
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