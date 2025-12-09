import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: API_BASE,
});

// Document APIs
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const listDocuments = () => api.get('/api/documents/list');
export const deleteDocument = (filename) => api.delete(`/api/documents/${filename}`);

// Connectors APIs
export const listConnectors = () => api.get('/api/connectors/');
export const configureConnector = (config) => api.post('/api/connectors/configure', config);
export const toggleConnector = (name) => api.post(`/api/connectors/${name}/toggle`);

// Chat API (non-streaming)
export const sendChat = (message, options = {}) => api.post('/api/chat/query', {
  message,
  use_documents: options.useDocuments ?? true,
  tools: options.tools || [],
  tool_params: options.toolParams || {}
});

// WebSocket connection for streaming
export const createChatSocket = () => {
  let base = API_BASE;
  if (!base) {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host; // e.g. localhost:5173
    // Backend is expected at 8000 in dev when not proxied
    const backendHost = host.includes(':') ? `${host.split(':')[0]}:8000` : host;
    return new WebSocket(`${proto}://${backendHost}/api/chat/ws`);
  }
  const proto = base.startsWith('https') ? 'wss' : 'ws';
  // Remove trailing slash
  base = base.replace(/\/$/, '');
  const wsUrl = `${proto}://${base.replace(/^https?:\/\//, '')}/api/chat/ws`;
  return new WebSocket(wsUrl);
};

// Settings APIs
export const setEmbeddingModel = (name) => api.post('/api/settings/embedding_model', { name });

// Conversations APIs
export const listConversations = () => api.get('/api/conversations/');
export const getConversation = (id) => api.get(`/api/conversations/${id}`);
export const getConversationMessages = (id) => api.get(`/api/conversations/${id}/messages`);
export const deleteConversation = (id) => api.delete(`/api/conversations/${id}`);
export const createConversation = () => api.post('/api/conversations/');
export const deleteAllConversations = () => api.delete('/api/conversations/');
export const renameConversation = (id, title) => api.post(`/api/conversations/${id}/rename`, { title });
