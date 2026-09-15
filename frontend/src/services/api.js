const API_BASE_URL = 'http://localhost:8000/api';

export async function sendChatMessage({ sessionId, message, llmProvider, apiKey }) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
      llm_provider: llmProvider,
      api_key: apiKey
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.statusText}`);
  }

  return await response.json();
}

export async function fetchSessions() {
  const response = await fetch(`${API_BASE_URL}/sessions`);
  if (!response.ok) {
    throw new Error('Failed to fetch sessions');
  }
  return await response.json();
}

export async function fetchSessionMessages(sessionId) {
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/messages`);
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return await response.json();
}