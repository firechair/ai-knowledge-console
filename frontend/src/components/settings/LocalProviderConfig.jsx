import React from 'react';

/**
 * Local provider configuration component (llama.cpp)
 */
export default function LocalProviderConfig({ config, onChange }) {
  const handleChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  return (
    <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
        Local Provider Configuration
      </h3>

      <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
        Configure your local llama.cpp server
      </div>

      {/* Base URL */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Server URL
        </label>
        <input
          type="url"
          value={config.base_url || 'http://localhost:8080'}
          onChange={(e) => handleChange('base_url', e.target.value)}
          placeholder="http://localhost:8080"
          className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100"
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Default: http://localhost:8080
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

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
        <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
          Quick Start
        </h4>
        <p className="text-xs text-blue-800 dark:text-blue-200">
          Run llama.cpp server with: <code className="bg-blue-100 dark:bg-blue-900/40 px-1 rounded">./llama-server -m model.gguf --port 8080</code>
        </p>
      </div>
    </div>
  );
}
