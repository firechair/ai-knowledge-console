import { useState, useEffect, useMemo } from 'react';
import { Github, Cloud, Bitcoin, Newspaper, Check, X, Settings, Mail, File, Slack, Book } from 'lucide-react';
import { listConnectors, configureConnector, toggleConnector, API_BASE } from '../utils/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const CONNECTOR_INFO = {
  github: { icon: Github, name: 'GitHub', needsKey: true },
  weather: { icon: Cloud, name: 'Weather', needsKey: true },
  crypto: { icon: Bitcoin, name: 'Crypto', needsKey: false },
  hackernews: { icon: Newspaper, name: 'Hacker News', needsKey: false },
  gmail: { icon: Mail, name: 'Gmail', oauth: true },
  drive: { icon: File, name: 'Google Drive', oauth: true },
  slack: { icon: Slack, name: 'Slack', oauth: true },
  notion: { icon: Book, name: 'Notion', oauth: true }
};

export default function Connectors({ onToolsChange }) {
  const [configuring, setConfiguring] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const queryClient = useQueryClient();

  const { data: connectors } = useQuery({
    queryKey: ['connectors'],
    queryFn: async () => {
      const res = await listConnectors();
      return res.data.connectors;
    }
  });

  const toggleMutation = useMutation({
    mutationFn: toggleConnector,
    onSuccess: () => {
      queryClient.invalidateQueries(['connectors']);
    }
  });

  const configureMutation = useMutation({
    mutationFn: configureConnector,
    onSuccess: () => {
      queryClient.invalidateQueries(['connectors']);
      setConfiguring(null);
      setApiKey('');
    }
  });

  // Update parent with enabled tools (stable identity)
  const enabledTools = useMemo(() => {
    if (!connectors) return [];
    return Object.entries(connectors)
      .filter(([_, v]) => v.enabled && v.configured)
      .map(([k]) => k);
  }, [connectors]);
  
  // Call parent callback when tools change
  useEffect(() => {
    onToolsChange?.(enabledTools);
  }, [enabledTools]);

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">API Connectors</h2>
      <p className="text-gray-600 mb-4">
        Enable external data sources to enhance AI responses
      </p>

      <div className="space-y-3">
        {connectors && Object.entries(connectors).map(([name, status]) => {
          const info = CONNECTOR_INFO[name];
          const Icon = info?.icon || Settings;
          
          return (
            <div
              key={name}
              className="bg-white border rounded-lg p-4"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Icon size={24} className="text-gray-600" />
                  <div>
                    <p className="font-medium">{info?.name || name}</p>
                    <p className="text-sm text-gray-500">
                      {status.configured ? (
                        <span className="text-green-600 flex items-center gap-1">
                          <Check size={14} /> Configured
                        </span>
                      ) : (
                        <span className="text-yellow-600">Needs configuration</span>
                      )}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {info?.needsKey && (
                    <button
                      onClick={() => setConfiguring(name)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Configure
                    </button>
                  )}
                  {info?.oauth && !status.configured && (
                    <button
                      onClick={() => {
                        const returnUrl = `${window.location.origin}#/connectors`;
                        const state = encodeURIComponent(JSON.stringify({ return_url: returnUrl }));
                        const provider = (name === 'gmail' || name === 'drive') ? 'google' : name;
                        let url = '';
                        if (!API_BASE) {
                          const proto = window.location.protocol.startsWith('https') ? 'https' : 'http';
                          const host = window.location.host;
                          const backendHost = host.includes(':') ? `${host.split(':')[0]}:8000` : host;
                          url = `${proto}://${backendHost}/api/auth/${provider}/login?state=${state}`;
                        } else {
                          const base = API_BASE.replace(/\/$/, '');
                          url = `${base}/api/auth/${provider}/login?state=${state}`;
                        }
                        window.location.href = url;
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Authorize
                    </button>
                  )}
                  <button
                    onClick={() => toggleMutation.mutate(name)}
                    className={`px-3 py-1 rounded-full text-sm ${
                      status.enabled
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                    disabled={!status.configured}
                  >
                    {status.enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              </div>

              {/* Configuration form */}
              {configuring === name && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="Enter API key"
                      className="flex-1 border rounded px-3 py-2"
                    />
                    <button
                      onClick={() => configureMutation.mutate({ name, api_key: apiKey })}
                      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setConfiguring(null)}
                      className="text-gray-500 px-2"
                    >
                      <X size={20} />
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
