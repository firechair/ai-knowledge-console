import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Send, Loader2, Sparkles, SlidersHorizontal, Plus } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { ChatMessage } from '../components/ui/ChatMessage';
import { createChatSocket, getConversationMessages, listConnectors, listDocuments } from '../utils/api';
import { Popover, PopoverTrigger, PopoverContent } from '../components/ui/Popover';

export default function ChatPage() {
    const { conversationId: urlConversationId } = useParams();
    const navigate = useNavigate();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Tool state
    const [useDocuments, setUseDocuments] = useState(true);
    const [enabledTools, setEnabledTools] = useState([]);
    const [availableConnectors, setAvailableConnectors] = useState({});
    const [availableDocuments, setAvailableDocuments] = useState([]);
    const [selectedDocuments, setSelectedDocuments] = useState([]);

    // Default tool parameters
    const [toolParams, setToolParams] = useState({
        github_repo: 'facebook/react',
        crypto_symbol: 'bitcoin',
        weather_city: 'London',
    });

    const messagesEndRef = useRef(null);
    const wsRef = useRef(null);
    const prevConversationIdRef = useRef(urlConversationId);

    // Initial load: History and Connectors
    useEffect(() => {
        const abortController = new AbortController();
        const prevConversationId = prevConversationIdRef.current;

        // Load history if conversation ID is in URL
        if (urlConversationId) {
            // Save to localStorage so we can restore it when navigating back
            localStorage.setItem('lastConversationId', urlConversationId);
            setIsLoading(true);
            setError(null);

            getConversationMessages(urlConversationId)
                .then(res => {
                    // Check if this request is still relevant
                    if (!abortController.signal.aborted) {
                        setMessages(res.data.messages.map(m => ({
                            role: m.role,
                            content: m.content,
                            sources: m.sources || []
                        })));
                    }
                })
                .catch(err => {
                    if (!abortController.signal.aborted) {
                        console.error("Failed to load history:", err);
                        setError("Failed to load conversation. It may have been deleted or doesn't exist.");
                        setMessages([]);
                    }
                })
                .finally(() => {
                    if (!abortController.signal.aborted) {
                        setIsLoading(false);
                    }
                });
        } else {
            // New chat - reset state
            setMessages([]);
            setError(null);
        }

        // Load global connectors
        listConnectors().then(res => {
            if (!abortController.signal.aborted) {
                const connectors = res.data.connectors || {};
                setAvailableConnectors(connectors);

                // Enable all properly configured and globally enabled connectors by default
                const globallyEnabled = Object.entries(connectors)
                    .filter(([_, status]) => status.enabled && status.configured)
                    .map(([name]) => name);

                setEnabledTools(globallyEnabled);
            }
        });

        // Load documents
        listDocuments().then(res => {
            if (!abortController.signal.aborted) {
                setAvailableDocuments(res.data.documents || []);
            }
        });

        // Cleanup function
        return () => {
            abortController.abort();

            // Only close WebSocket if conversation ID is actually changing to a different value
            // (not just navigating away temporarily)
            const isConversationChanging = prevConversationId !== urlConversationId &&
                urlConversationId !== undefined;

            if (wsRef.current?.readyState === WebSocket.OPEN && isConversationChanging) {
                wsRef.current.close();
            }

            // Update ref for next cleanup
            prevConversationIdRef.current = urlConversationId;
        };
    }, [urlConversationId]);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Socket logic
    const ensureSocket = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return wsRef.current;

        const socket = createChatSocket();
        wsRef.current = socket;

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'start') {
                setMessages(prev => [...prev, { role: 'assistant', content: '', sources: [] }]);
            } else if (data.type === 'token') {
                setMessages(prev => {
                    const updated = [...prev];
                    const last = updated[updated.length - 1];
                    updated[updated.length - 1] = { ...last, content: last.content + data.content };
                    return updated;
                });
            } else if (data.type === 'end') {
                setIsLoading(false);
                if (data.conversation_id) {
                    // Update URL to include conversation ID (only if not already there)
                    if (!urlConversationId) {
                        navigate(`/chat/${data.conversation_id}`, { replace: true });
                    }
                }
                if (data.sources) {
                    setMessages(prev => {
                        const updated = [...prev];
                        const last = updated[updated.length - 1];
                        updated[updated.length - 1] = { ...last, sources: data.sources };
                        return updated;
                    });
                }
            } else if (data.type === 'api_data') {
                // Should we show this? For now, maybe just log or handle if desired
                // The assistant message will contain the interpreted data
            }
        };
        return socket;
    };

    const handleSend = () => {
        if (!input.trim() || isLoading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setIsLoading(true);
        setInput('');

        const socket = ensureSocket();
        const payload = JSON.stringify({
            message: input,
            use_documents: useDocuments,
            selected_documents: selectedDocuments.length > 0 ? selectedDocuments : null,
            tools: enabledTools,
            tool_params: toolParams,
            conversation_id: urlConversationId
        });

        if (socket.readyState === WebSocket.OPEN) {
            socket.send(payload);
        } else {
            socket.onopen = () => socket.send(payload);
        }
    };

    const startNewChat = () => {
        setMessages([]);
        setError(null);
        // Clear last conversation from localStorage
        localStorage.removeItem('lastConversationId');
        // Navigate to root for new chat
        navigate('/', { replace: true });
    };

    const handleToolToggle = (toolName, isConfigured) => {
        // Allow toggling if it's configured OR it's a public tool (crypto/hackernews)
        const isPublic = ['crypto', 'hackernews'].includes(toolName);
        
        if (!isConfigured && !isPublic) {
            alert(`Please configure the ${toolName} connector in the Connectors page to use this tool.`);
            return;
        }

        setEnabledTools(prev =>
            prev.includes(toolName)
                ? prev.filter(t => t !== toolName)
                : [...prev, toolName]
        );
    };

    const handleDocumentToggle = (docName) => {
        setSelectedDocuments(prev =>
            prev.includes(docName)
                ? prev.filter(d => d !== docName)
                : [...prev, docName]
        );
    };

    return (
        <div className="flex h-full w-full">
            <div className="flex-1 flex flex-col glass-card rounded-2xl overflow-hidden relative">
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-red-600 dark:text-red-400">
                            <p className="font-medium">{error}</p>
                            <Button variant="ghost" size="sm" className="mt-2" onClick={startNewChat}>
                                Start New Chat
                            </Button>
                        </div>
                    )}
                    {!error && messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-[rgb(var(--text-secondary))] opacity-80">
                            <img 
                                src="/logo-light.jpg" 
                                alt="Logo" 
                                className="w-24 h-24 object-contain mb-6 block dark:hidden"
                            />
                            <img 
                                src="/logo-dark.jpg" 
                                alt="Logo" 
                                className="w-24 h-24 object-contain mb-6 hidden dark:block"
                            />
                            <p className="text-lg font-medium">How can I help you today?</p>
                        </div>
                    ) : (
                        !error && messages.map((m, i) => (
                            <ChatMessage key={i} {...m} />
                        ))
                    )}
                    {isLoading && messages[messages.length - 1]?.role === 'user' && (
                        <div className="flex items-center gap-2 p-4 text-sm text-[rgb(var(--text-secondary))] animate-pulse">
                            <Loader2 className="animate-spin" size={16} /> Thinking...
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Floating Input Area */}
                <div className="p-4 bg-gradient-to-t from-[rgb(var(--bg-card))] to-transparent">
                    <div className="glass rounded-xl p-2 flex items-center gap-2 shadow-sm ring-1 ring-[rgb(var(--border-color))] focus-within:ring-2 focus-within:ring-[rgb(var(--accent-primary))] transition-all">
                        <Popover>
                            <PopoverTrigger asChild>
                                <Button variant="ghost" size="icon" className="hover:text-[rgb(var(--accent-primary))]">
                                    <SlidersHorizontal size={20} />
                                </Button>
                            </PopoverTrigger>

                            <PopoverContent align="start" side="top" alignOffset={-10} sideOffset={10} className="w-80">
                                {/* Header */}
                                <div className="p-4 border-b border-[rgb(var(--border-color))] flex justify-between items-center">
                                    <span className="font-semibold text-sm">Configuration</span>
                                    <Button variant="ghost" size="icon" onClick={startNewChat} title="New Chat">
                                        <Plus size={18} />
                                    </Button>
                                </div>

                                {/* Controls */}
                                <div className="p-4 space-y-6 max-h-[60vh] overflow-auto">
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between">
                                            <label className="text-xs font-semibold uppercase tracking-wider text-[rgb(var(--text-secondary))]">
                                                Context
                                            </label>
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs text-[rgb(var(--text-secondary))]">RAG</span>
                                                <input
                                                    type="checkbox"
                                                    className="toggle toggle-sm"
                                                    checked={useDocuments}
                                                    onChange={e => setUseDocuments(e.target.checked)}
                                                />
                                            </div>
                                        </div>
                                        
                                        {useDocuments && (
                                            <div className="border border-[rgb(var(--border-color))] rounded-lg overflow-hidden">
                                                <div className="bg-[rgb(var(--bg-app))]/50 p-2 text-xs font-medium text-[rgb(var(--text-secondary))] border-b border-[rgb(var(--border-color))]">
                                                    Select Documents (Default: All)
                                                </div>
                                                <div className="max-h-40 overflow-y-auto p-1 space-y-1">
                                                    {availableDocuments.length === 0 ? (
                                                        <div className="p-3 text-center text-xs text-[rgb(var(--text-secondary))]">
                                                            No documents uploaded yet.
                                                        </div>
                                                    ) : (
                                                        availableDocuments.map(doc => (
                                                            <div 
                                                                key={doc} 
                                                                onClick={() => handleDocumentToggle(doc)}
                                                                className={`
                                                                    flex items-center gap-2 p-2 rounded cursor-pointer text-sm transition-colors
                                                                    ${selectedDocuments.includes(doc) 
                                                                        ? 'bg-[rgb(var(--accent-primary))]/10 text-[rgb(var(--accent-primary))]' 
                                                                        : 'hover:bg-[rgb(var(--text-secondary))]/10'
                                                                    }
                                                                `}
                                                            >
                                                                <div className={`
                                                                    w-4 h-4 rounded border flex items-center justify-center
                                                                    ${selectedDocuments.includes(doc)
                                                                        ? 'bg-[rgb(var(--accent-primary))] border-[rgb(var(--accent-primary))]'
                                                                        : 'border-[rgb(var(--text-secondary))]/50'
                                                                    }
                                                                `}>
                                                                    {selectedDocuments.includes(doc) && <Sparkles size={10} className="text-white" />}
                                                                </div>
                                                                <span className="truncate">{doc}</span>
                                                            </div>
                                                        ))
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    <div className="space-y-3">
                                        <label className="text-xs font-semibold uppercase tracking-wider text-[rgb(var(--text-secondary))]">
                                            Tools
                                        </label>
                                        <div className="border border-[rgb(var(--border-color))] rounded-lg overflow-hidden">
                                            {Object.keys(availableConnectors).length === 0 ? (
                                                <div className="p-4 text-center text-xs text-[rgb(var(--text-secondary))]">
                                                    No tools configured.
                                                </div>
                                            ) : (
                                                Object.entries(availableConnectors).map(([name, status]) => (
                                                    <div 
                                                        key={name} 
                                                        onClick={() => handleToolToggle(name, status.configured)}
                                                        className={`
                                                            flex items-center justify-between p-3 border-b border-[rgb(var(--border-color))] last:border-0 cursor-pointer transition-colors
                                                            ${enabledTools.includes(name) 
                                                                ? 'bg-[rgb(var(--accent-primary))]/5' 
                                                                : 'hover:bg-[rgb(var(--text-secondary))]/5'
                                                            }
                                                            ${(!status.configured && !['crypto', 'hackernews'].includes(name)) ? 'opacity-60 grayscale' : ''}
                                                        `}
                                                    >
                                                        <span className="text-sm capitalize">{name.replace('_', ' ')}</span>
                                                        <div className={`
                                                            w-9 h-5 rounded-full relative transition-colors duration-200
                                                            ${enabledTools.includes(name) ? 'bg-[rgb(var(--accent-primary))]' : 'bg-gray-200 dark:bg-zinc-700'}
                                                        `}>
                                                            <div className={`
                                                                absolute top-1 left-1 w-3 h-3 rounded-full bg-white transition-transform duration-200
                                                                ${enabledTools.includes(name) ? 'translate-x-4' : 'translate-x-0'}
                                                            `} />
                                                        </div>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </PopoverContent>
                        </Popover>
                        <input
                            className="flex-1 bg-transparent border-none outline-none px-2 text-sm placeholder:text-[rgb(var(--text-secondary))]"
                            placeholder="Type a message..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSend()}
                            autoFocus
                        />
                        <Button size="icon" onClick={handleSend} disabled={isLoading || !input.trim()} className="rounded-lg">
                            <Send size={18} />
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
