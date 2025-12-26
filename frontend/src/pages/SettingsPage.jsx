import { useState } from 'react';
import { LLMProviderSelector } from '../components/settings/LLMProviderSelector';
import { ModelManager } from '../components/settings/ModelManager';
import APIKeysManager from '../components/settings/APIKeysManager';
import { Settings, Database, Server, Key } from 'lucide-react';
import { cn } from '../utils/cn';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('provider');

  const tabs = [
    { id: 'provider', label: 'LLM Provider', icon: Server, description: 'Configure API connections and provider settings' },
    { id: 'api-keys', label: 'API Keys', icon: Key, description: 'Manage API keys for cloud providers and connectors' },
    { id: 'models', label: 'Model Management', icon: Database, description: 'Download and manage local models and embeddings' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-6">
      <div>
        <h1 className="text-3xl font-bold text-[rgb(var(--text-primary))] flex items-center gap-3">
          <Settings className="w-8 h-8 text-[rgb(var(--accent-primary))]" />
          Settings
        </h1>
        <p className="text-[rgb(var(--text-secondary))] mt-2 text-lg">
          Manage your AI configuration and resources.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:w-64 flex-shrink-0 space-y-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-left",
                activeTab === tab.id
                  ? "bg-[rgb(var(--accent-primary))]/10 text-[rgb(var(--accent-primary))] font-medium ring-1 ring-[rgb(var(--accent-primary))]/20"
                  : "text-[rgb(var(--text-secondary))] hover:bg-[rgb(var(--bg-card-hover))] hover:text-[rgb(var(--text-primary))]"
              )}
            >
              <tab.icon size={18} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* content Area */}
        <div className="flex-1 min-w-0">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-[rgb(var(--text-primary))]">
              {tabs.find(t => t.id === activeTab)?.label}
            </h2>
            <p className="text-sm text-[rgb(var(--text-secondary))]">
              {tabs.find(t => t.id === activeTab)?.description}
            </p>
          </div>

          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            {activeTab === 'provider' && <LLMProviderSelector />}
            {activeTab === 'api-keys' && <APIKeysManager />}
            {activeTab === 'models' && <ModelManager />}
          </div>
        </div>
      </div>
    </div>
  );
}
