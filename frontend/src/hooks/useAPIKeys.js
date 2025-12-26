import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Hook to manage API keys (status and updates)
 */
export function useAPIKeys() {
  const [apiKeys, setApiKeys] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null);

  const fetchAPIKeysStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/api-keys/status`);
      setApiKeys(response.data.api_keys || {});
    } catch (err) {
      console.error('Failed to fetch API keys status:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAPIKeysStatus();
  }, []);

  const saveAPIKeys = async (keys) => {
    try {
      setSaveStatus('saving');
      const response = await axios.post(`${API_URL}/api/api-keys/`, keys);
      setSaveStatus('success');

      // Refresh the status after saving
      await fetchAPIKeysStatus();

      return { success: true, message: response.data.message };
    } catch (err) {
      console.error('Failed to save API keys:', err);
      setSaveStatus('error');
      return {
        success: false,
        message: err.response?.data?.detail || err.message
      };
    }
  };

  const deleteAPIKey = async (service) => {
    try {
      await axios.delete(`${API_URL}/api/api-keys/${service}`);

      // Refresh the status after deletion
      await fetchAPIKeysStatus();

      return { success: true };
    } catch (err) {
      console.error(`Failed to delete API key for ${service}:`, err);
      return {
        success: false,
        message: err.response?.data?.detail || err.message
      };
    }
  };

  return {
    apiKeys,
    loading,
    error,
    saveStatus,
    saveAPIKeys,
    deleteAPIKey,
    refresh: fetchAPIKeysStatus
  };
}
