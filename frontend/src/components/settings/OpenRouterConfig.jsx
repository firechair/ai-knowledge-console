import React from 'react';
import { useOpenRouterModels } from '../../hooks/useCloudProviders';

/**
 * OpenRouter-specific configuration component
 */
export default function OpenRouterConfig({ config, onChange }) {
  const { models, loading, error } = useOpenRouterModels();

  const handleChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  // Group models by free/paid
  const freeModels = models.filter(m => m.is_free);
  const paidModels = models.filter(m => !m.is_free);

  return (
    <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
        OpenRouter Configuration
      </h3>

      {/* Model Selection */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Model *
          </label>
          <button
            onClick={() => window.location.reload()} // Ideally this would trigger a refetch hook but simple reload works for now or we trigger a mutate
            className="text-xs text-blue-600 hover:text-blue-800"
            title="Refresh list"
          >
            Refresh Models
          </button>
        </div>

        {loading ? (
          <div className="text-sm text-gray-500">Loading models...</div>
        ) : error ? (
          <div className="text-sm text-red-500">Failed to load models</div>
        ) : (
          <div className="relative">
            <input
              list="openrouter-models"
              value={config.model || ''}
              onChange={(e) => handleChange('model', e.target.value)}
              placeholder="Select or type model ID..."
              className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-gray-100"
            />
            <datalist id="openrouter-models">
              {freeModels.length > 0 && (
                freeModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} (Free)
                  </option>
                ))
              )}
              {paidModels.length > 0 && (
                paidModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))
              )}
            </datalist>
            <p className="text-xs text-gray-500 mt-1">
              Select from list or type custom model ID (e.g. anthropic/claude-3-opus)
            </p>
          </div>
        )}
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

      {/* Advanced Parameters */}
      <details className="space-y-3">
        <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300">
          Advanced Parameters
        </summary>
        <div className="space-y-3 pt-3">
          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
              Top P: {config.top_p ?? 0.9}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={config.top_p ?? 0.9}
              onChange={(e) => handleChange('top_p', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
              Frequency Penalty: {config.frequency_penalty ?? 0.2}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.frequency_penalty ?? 0.2}
              onChange={(e) => handleChange('frequency_penalty', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
              Presence Penalty: {config.presence_penalty ?? 0.0}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.presence_penalty ?? 0.0}
              onChange={(e) => handleChange('presence_penalty', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
              Repetition Penalty: {config.repetition_penalty ?? 1.1}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.repetition_penalty ?? 1.1}
              onChange={(e) => handleChange('repetition_penalty', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      </details>
    </div>
  );
}
