import React from 'react';

/**
 * Provider Type Selector - allows choosing between Cloud and Local providers
 */
export default function ProviderTypeSelector({ value, onChange }) {
  const providerTypes = [
    {
      id: 'cloud',
      name: 'Cloud Provider',
      description: 'Use hosted AI services (OpenRouter, OpenAI, or custom)',
      icon: '☁️'
    },
    {
      id: 'local',
      name: 'Local',
      description: 'Self-hosted llama.cpp server',
      icon: '💻'
    }
  ];

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Provider Type
      </label>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {providerTypes.map((type) => (
          <button
            key={type.id}
            type="button"
            onClick={() => onChange(type.id)}
            className={`
              relative flex flex-col items-start p-4 rounded-lg border-2 transition-all
              ${value === type.id
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }
            `}
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{type.icon}</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {type.name}
              </span>
              {value === type.id && (
                <span className="ml-auto text-blue-500">✓</span>
              )}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 text-left">
              {type.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
