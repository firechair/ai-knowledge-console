import React from 'react';
import { useCloudProviders } from '../../hooks/useCloudProviders';

/**
 * Cloud Provider Selector - allows choosing between OpenRouter, OpenAI, or Custom
 */
export default function CloudProviderSelector({ value, onChange }) {
  const { providers, loading, error } = useCloudProviders();

  if (loading) {
    return (
      <div className="text-sm text-gray-500 dark:text-gray-400">
        Loading cloud providers...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-sm text-red-500">
        Failed to load cloud providers: {error}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Cloud Provider
      </label>
      <div className="grid grid-cols-1 gap-3">
        {providers.map((provider) => (
          <button
            key={provider.id}
            type="button"
            onClick={() => onChange(provider.id)}
            className={`
              flex flex-col items-start p-4 rounded-lg border-2 transition-all text-left
              ${value === provider.id
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }
            `}
          >
            <div className="flex items-center justify-between w-full mb-1">
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {provider.name}
              </span>
              <div className="flex items-center gap-2">
                {provider.has_free_tier && (
                  <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-0.5 rounded">
                    Free Tier
                  </span>
                )}
                {value === provider.id && (
                  <span className="text-blue-500">✓</span>
                )}
              </div>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {provider.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
