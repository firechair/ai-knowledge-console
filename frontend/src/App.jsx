import { useState, useEffect, useRef } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MessageSquare, FileText, Plug, Settings as SettingsIcon } from 'lucide-react';
import Chat from './components/Chat';
import DocumentUpload from './components/DocumentUpload';
import Connectors from './components/Connectors';
import Settings from './components/Settings';
import ErrorBoundary from './components/ErrorBoundary';
import ConversationList from './components/ConversationList';

const queryClient = new QueryClient();

function AppContent() {
  const [activeTab, setActiveTab] = useState('chat');
  const [enabledTools, setEnabledTools] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [toolParams, setToolParams] = useState({
    github_repo: 'facebook/react',
    crypto_symbol: 'bitcoin',
    weather_city: 'London'
  });

  const tabs = [
    { id: 'chat', label: 'Chat', icon: MessageSquare, shortcut: '⌘1' },
    { id: 'documents', label: 'Documents', icon: FileText, shortcut: '⌘2' },
    { id: 'connectors', label: 'Connectors', icon: Plug, shortcut: '⌘3' },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, shortcut: '⌘4' }
  ];

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Tab navigation: Cmd/Ctrl + 1-4
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
        const num = parseInt(e.key);
        if (num >= 1 && num <= 4) {
          e.preventDefault();
          setActiveTab(tabs[num - 1].id);
        }
      }

      // Escape: Clear selections
      if (e.key === 'Escape') {
        setSelectedConversation(null);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

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
        <nav className="w-64 bg-white border-r border-gray-200 p-4" role="navigation" aria-label="Main navigation">
          <ul className="space-y-2" role="menubar">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <li key={tab.id} role="none">
                  <button
                    onClick={() => setActiveTab(tab.id)}
                    role="menuitem"
                    aria-label={`${tab.label} (${tab.shortcut})`}
                    aria-current={activeTab === tab.id ? 'page' : undefined}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${activeTab === tab.id
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-50'
                      }`}
                  >
                    <span className="flex items-center gap-3">
                      <Icon size={20} />
                      {tab.label}
                    </span>
                    <span className="text-xs text-gray-400">{tab.shortcut}</span>
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
        <main className="flex-1 bg-gray-50 flex" role="main">
          {activeTab === 'chat' && (
            <>
              <ConversationList
                onSelectConversation={setSelectedConversation}
                selectedId={selectedConversation}
              />
              <div className="flex-1">
                <Chat
                  enabledTools={enabledTools}
                  toolParams={toolParams}
                  conversationId={selectedConversation}
                />
              </div>
            </>
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
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
