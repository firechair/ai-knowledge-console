import React from 'react';

/**
 * Custom OpenAI-compatible provider configuration component
 */
export default function CustomProviderConfig({ config, onChange }) {
  const handleChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  return (
    <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
        Custom Provider Configuration
      </h3>

      <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
        Configure any OpenAI-compatible API endpoint (e.g., LM Studio, Ollama, LocalAI)
      </div>

      {/* Base URL */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Base URL *
        </label>
        <input
          type="url"
          value={config.base_url || ''}
          onChange={(e) => handleChange('base_url', e.target.value)}
          placeholder="http://localhost:1234/v1"
          className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100"
          required
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Include /v1 at the end if required by your provider
        </p>
      </div>

      {/* Model */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Model ID *
        </label>
        <input
          type="text"
          value={config.model || ''}
          onChange={(e) => handleChange('model', e.target.value)}
          placeholder="e.g., llama-3.3-70b-instruct"
          className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100"
          required
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          The model identifier as expected by your provider
        </p>
      </div>

      {/* Temperature */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Temperature: {config.temperature ?? 0.7}
        </label>
        <input
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={config.temperature ?? 0.7}
          onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>Focused (0)</span>
          <span>Balanced (1)</span>
          <span>Creative (2)</span>
        </div>
      </div>

      {/* Max Tokens */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Max Tokens
        </label>
        <input
          type="number"
          value={config.max_tokens ?? 1024}
          onChange={(e) => handleChange('max_tokens', parseInt(e.target.value))}
          className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100"
          min="1"
          max="100000"
        />
      </div>
    </div>
  );
}
