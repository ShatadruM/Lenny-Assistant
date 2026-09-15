import React, { useState } from 'react';
import { ChatProvider, useChat } from './context/ChatContext';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import ChatContainer from './components/chat/ChatContainer';
import ChatInput from './components/chat/ChatInput';
import ArtifactViewer from './components/artifacts/ArtifactViewer';
import ApiKeyModal from './components/layout/ApiKeyModal';
import LandingPage from './components/auth/LandingPage';
import './App.css';

function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user } = useChat();

  if (!user) {
    return <LandingPage />;
  }

  return (
    <div className="app-layout">
      {/* Ambient orange grain/gradient backdrop — sits behind every panel */}
      <div className="ambient-backdrop">
        <div className="ambient-glow glow-1" />
        <div className="ambient-glow glow-2" />
        <div className="ambient-glow glow-3" />
        <div className="ambient-noise" />
      </div>

      <Header sidebarOpen={sidebarOpen} onToggleSidebar={() => setSidebarOpen((v) => !v)} />

      <div className="main-content-wrapper">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="chat-main-area">
          <ChatContainer />
          <ChatInput />
        </main>

        <ArtifactViewer />
      </div>
      <ApiKeyModal />
    </div>
  );
}

export default function App() {
  return (
    <ChatProvider>
      <MainLayout />
    </ChatProvider>
  );
}