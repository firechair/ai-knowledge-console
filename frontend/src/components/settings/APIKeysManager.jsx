import React, { useState } from 'react';
import { useAPIKeys } from '../../hooks/useAPIKeys';

/**
 * API Keys Manager - allows users to set and manage API keys for various services
 */
export default function APIKeysManager() {
  const { apiKeys, loading, saveAPIKeys, saveStatus } = useAPIKeys();
  const [formData, setFormData] = useState({});
  const [showKeys, setShowKeys] = useState({});
  const [message, setMessage] = useState(null);

  const services = [
    {
      key: 'openrouter',
      name: 'OpenRouter',
      description: 'Required for OpenRouter cloud provider',
      link: 'https://openrouter.ai/keys'
    },
    {
      key: 'openai',
      name: 'OpenAI',
      description: 'Required for OpenAI cloud provider',
      link: 'https://platform.openai.com/api-keys'
    },
    {
      key: 'github_token',
      name: 'GitHub Token',
      description: 'For GitHub API connector',
      link: 'https://github.com/settings/tokens'
    },
    {
      key: 'openweather_api_key',
      name: 'OpenWeather API',
      description: 'For weather data connector',
      link: 'https://openweathermap.org/api'
    },
    {
      key: 'crypto_api_key',
      name: 'Crypto API',
      description: 'For cryptocurrency data connector',
      link: null
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);

    // Filter out empty values
    const keysToSave = Object.fromEntries(
      Object.entries(formData).filter(([_, value]) => value && value.trim())
    );

    if (Object.keys(keysToSave).length === 0) {
      setMessage({ type: 'error', text: 'Please enter at least one API key' });
      return;
    }

    const result = await saveAPIKeys(keysToSave);

    if (result.success) {
      setMessage({ type: 'success', text: result.message });
      setFormData({});
    } else {
      setMessage({ type: 'error', text: result.message });
    }
  };

  const toggleShowKey = (key) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
  };

  if (loading) {
    return <div className="text-sm text-gray-500">Loading API keys...</div>;
  }

  return (
    <div className="space-y-4">
      {message && (
        <div className={`
          p-3 rounded-lg border
          ${message.type === 'success'
            ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200'
            : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200'
          }
        `}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {services.map(service => (
          <div key={service.key} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                  {service.name}
                  {apiKeys[service.key] && (
                    <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-0.5 rounded">
                      ✓ Set
                    </span>
                  )}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {service.description}
                </p>
              </div>
              {service.link && (
                <a
                  href={service.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Get Key →
                </a>
              )}
            </div>

            <div className="relative">
              <input
                type={showKeys[service.key] ? 'text' : 'password'}
                value={formData[service.key] || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, [service.key]: e.target.value }))}
                placeholder={apiKeys[service.key] ? '••••••••••••••••' : 'Enter API key...'}
                className="w-full px-3 py-2 pr-10 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100"
              />
              <button
                type="button"
                onClick={() => toggleShowKey(service.key)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                {showKeys[service.key] ? '🙈' : '👁️'}
              </button>
            </div>
          </div>
        ))}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saveStatus === 'saving'}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saveStatus === 'saving' ? 'Saving...' : 'Save API Keys'}
          </button>

          {Object.keys(formData).length > 0 && (
            <button
              type="button"
              onClick={() => setFormData({})}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Clear
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
