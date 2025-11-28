import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MessageSquare, FileText, Plug, Settings as SettingsIcon } from 'lucide-react';
import Chat from './components/Chat';
import DocumentUpload from './components/DocumentUpload';
import Connectors from './components/Connectors';
import Settings from './components/Settings';

const queryClient = new QueryClient();

function AppContent() {
  const [activeTab, setActiveTab] = useState('chat');
  const [enabledTools, setEnabledTools] = useState([]);
  const [toolParams, setToolParams] = useState({
    github_repo: 'facebook/react',
    crypto_symbol: 'bitcoin',
    weather_city: 'London'
  });

  const tabs = [
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'connectors', label: 'Connectors', icon: Plug },
    { id: 'settings', label: 'Settings', icon: SettingsIcon }
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-800">
          AI Knowledge Console
        </h1>
        <p className="text-gray-500 text-sm">
          RAG + External APIs • Powered by Local LLM
        </p>
      </header>

      {/* Main content */}
      <div className="flex-1 flex">
        {/* Sidebar */}
        <nav className="w-64 bg-white border-r border-gray-200 p-4">
          <ul className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <li key={tab.id}>
                  <button
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon size={20} />
                    {tab.label}
                  </button>
                </li>
              );
            })}
          </ul>

          {/* Tool params (when on chat) */}
          {activeTab === 'chat' && enabledTools.length > 0 && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium mb-2">Tool Parameters</h3>
              {enabledTools.includes('github') && (
                <input
                  type="text"
                  value={toolParams.github_repo}
                  onChange={(e) => setToolParams(p => ({ ...p, github_repo: e.target.value }))}
                  placeholder="GitHub repo"
                  className="w-full mb-2 text-sm border rounded px-2 py-1"
                />
              )}
              {enabledTools.includes('crypto') && (
                <input
                  type="text"
                  value={toolParams.crypto_symbol}
                  onChange={(e) => setToolParams(p => ({ ...p, crypto_symbol: e.target.value }))}
                  placeholder="Crypto symbol"
                  className="w-full mb-2 text-sm border rounded px-2 py-1"
                />
              )}
              {enabledTools.includes('weather') && (
                <input
                  type="text"
                  value={toolParams.weather_city}
                  onChange={(e) => setToolParams(p => ({ ...p, weather_city: e.target.value }))}
                  placeholder="City"
                  className="w-full text-sm border rounded px-2 py-1"
                />
              )}
            </div>
          )}
        </nav>

        {/* Content area */}
        <main className="flex-1 bg-gray-50">
          {activeTab === 'chat' && (
            <Chat enabledTools={enabledTools} toolParams={toolParams} />
          )}
          {activeTab === 'documents' && <DocumentUpload />}
          {activeTab === 'connectors' && (
            <Connectors onToolsChange={setEnabledTools} />
          )}
          {activeTab === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
