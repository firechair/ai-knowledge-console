import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

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
  const wsUrl = API_BASE.replace('http', 'ws') + '/api/chat/ws';
  return new WebSocket(wsUrl);
};
