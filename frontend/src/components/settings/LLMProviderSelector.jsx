import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Loader2, Check, AlertTriangle } from 'lucide-react';
import ProviderTypeSelector from './ProviderTypeSelector';
import CloudProviderSelector from './CloudProviderSelector';
import OpenRouterConfig from './OpenRouterConfig';
import OpenAIConfig from './OpenAIConfig';
import CustomProviderConfig from './CustomProviderConfig';
import LocalProviderConfig from './LocalProviderConfig';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function LLMProviderSelector({ onSave }) {
  const [providerType, setProviderType] = useState('cloud');
  const [cloudProvider, setCloudProvider] = useState('openrouter');
  const [cloudConfigs, setCloudConfigs] = useState({
    openrouter: { model: '', temperature: 0.7, max_tokens: 1024 },
    openai: { model: '', temperature: 0.7, max_tokens: 1024 },
    custom: { base_url: '', model: '', temperature: 0.7, max_tokens: 1024 }
  });
  const [localConfig, setLocalConfig] = useState({
    base_url: 'http://localhost:8080',
    temperature: 0.7,
    max_tokens: 1024
  });
  const [loading, setLoading] = useState(false);
  const [loadingSettings, setLoadingSettings] = useState(true);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    // Load current settings
    const loadSettings = async () => {
      try {
        const response = await fetch(`${API_URL}/api/settings/llm`);
        const data = await response.json();

        if (data.config) {
          const config = data.config;

          // Check if using new format
          if (config.provider_type) {
            setProviderType(config.provider_type);

            if (config.provider_type === 'cloud') {
              setCloudProvider(config.cloud_provider);

              // Load the relevant cloud config
              if (config.cloud_provider && config.model) {
                setCloudConfigs(prev => ({
                  ...prev,
                  [config.cloud_provider]: {
                    model: config.model,
                    temperature: config.temperature ?? 0.7,
                    max_tokens: config.max_tokens ?? 1024,
                    // OpenRouter-specific
                    ...(config.cloud_provider === 'openrouter' && {
                      top_p: config.top_p ?? 0.9,
                      frequency_penalty: config.frequency_penalty ?? 0.2,
                      presence_penalty: config.presence_penalty ?? 0.0,
                      repetition_penalty: config.repetition_penalty ?? 1.1
                    }),
                    // Custom provider-specific
                    ...(config.cloud_provider === 'custom' && {
                      base_url: config.base_url ?? ''
                    })
                  }
                }));
              }
            } else if (config.provider_type === 'local') {
              setLocalConfig({
                base_url: config.base_url ?? 'http://localhost:8080',
                temperature: config.temperature ?? 0.7,
                max_tokens: config.max_tokens ?? 1024
              });
            }
          }
          // Backward compatibility with old format
          else if (config.provider) {
            const oldProvider = config.provider;
            if (oldProvider === 'openrouter') {
              setProviderType('cloud');
              setCloudProvider('openrouter');
              setCloudConfigs(prev => ({
                ...prev,
                openrouter: {
                  model: config.model ?? '',
                  temperature: config.temperature ?? 0.7,
                  max_tokens: config.max_tokens ?? 1024,
                  top_p: config.top_p ?? 0.9,
                  frequency_penalty: config.frequency_penalty ?? 0.2,
                  presence_penalty: config.presence_penalty ?? 0.0,
                  repetition_penalty: config.repetition_penalty ?? 1.1
                }
              }));
            } else if (oldProvider === 'openai-compatible') {
              setProviderType('cloud');
              setCloudProvider('custom');
              setCloudConfigs(prev => ({
                ...prev,
                custom: {
                  base_url: config.base_url ?? '',
                  model: config.model ?? '',
                  temperature: config.temperature ?? 0.7,
                  max_tokens: config.max_tokens ?? 1024
                }
              }));
            } else if (oldProvider === 'local') {
              setProviderType('local');
              setLocalConfig({
                base_url: config.base_url ?? 'http://localhost:8080',
                temperature: config.temperature ?? 0.7,
                max_tokens: config.max_tokens ?? 1024
              });
            }
          }
        }
      } catch (err) {
        console.error('Failed to load settings:', err);
      } finally {
        setLoadingSettings(false);
      }
    };

    loadSettings();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setStatus(null);

    try {
      let payload;

      if (providerType === 'cloud') {
        const currentCloudConfig = cloudConfigs[cloudProvider];

        // Validate required fields
        if (!currentCloudConfig.model) {
          throw new Error('Please select a model');
        }
        if (cloudProvider === 'custom' && !currentCloudConfig.base_url) {
          throw new Error('Please provide a base URL for custom provider');
        }

        payload = {
          provider_type: 'cloud',
          cloud_provider: cloudProvider,
          cloud_service_config: {
            [cloudProvider]: currentCloudConfig
          }
        };
      } else {
        // Local provider
        if (!localConfig.base_url) {
          throw new Error('Please provide a base URL for local provider');
        }

        payload = {
          provider_type: 'local',
          local: localConfig
        };
      }

      const response = await fetch(`${API_URL}/api/settings/llm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save settings');
      }

      setStatus({ type: 'success', message: 'Settings saved! Restart backend to apply.' });
      if (onSave) onSave();
    } catch (error) {
      setStatus({ type: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  if (loadingSettings) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Loading settings...</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>LLM Provider Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Provider Type Selection */}
        <ProviderTypeSelector
          value={providerType}
          onChange={setProviderType}
        />

        {/* Cloud Provider Selection */}
        {providerType === 'cloud' && (
          <>
            <CloudProviderSelector
              value={cloudProvider}
              onChange={setCloudProvider}
            />

            {/* Cloud Provider-specific Configuration */}
            {cloudProvider === 'openrouter' && (
              <OpenRouterConfig
                config={cloudConfigs.openrouter}
                onChange={(newConfig) => setCloudConfigs(prev => ({ ...prev, openrouter: newConfig }))}
              />
            )}

            {cloudProvider === 'openai' && (
              <OpenAIConfig
                config={cloudConfigs.openai}
                onChange={(newConfig) => setCloudConfigs(prev => ({ ...prev, openai: newConfig }))}
              />
            )}

            {cloudProvider === 'custom' && (
              <CustomProviderConfig
                config={cloudConfigs.custom}
                onChange={(newConfig) => setCloudConfigs(prev => ({ ...prev, custom: newConfig }))}
              />
            )}
          </>
        )}

        {/* Local Provider Configuration */}
        {providerType === 'local' && (
          <LocalProviderConfig
            config={localConfig}
            onChange={setLocalConfig}
          />
        )}

        {/* Status Message */}
        {status && (
          <div className={`flex items-center space-x-2 p-3 rounded-lg ${
            status.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300' :
            'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300'
          }`}>
            {status.type === 'success' ? <Check size={16} /> : <AlertTriangle size={16} />}
            <span className="text-sm">{status.message}</span>
          </div>
        )}

        {/* Save Button */}
        <Button onClick={handleSave} disabled={loading} className="w-full">
          {loading && <Loader2 size={16} className="mr-2 animate-spin" />}
          Save Settings
        </Button>
      </CardContent>
    </Card>
  );
}
