import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, FileText, Globe } from 'lucide-react';
import { createChatSocket, getConversationMessages } from '../utils/api';

export default function Chat({ enabledTools = [], toolParams = {}, conversationIdProp = null }) {
  const STORAGE_KEY = 'akconsole_chat_state';
  const getSaved = () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {};
    }
  };
  const saved = getSaved();
  const [messages, setMessages] = useState(() => Array.isArray(saved.messages) ? saved.messages : []);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useDocuments, setUseDocuments] = useState(() => typeof saved.useDocuments === 'boolean' ? saved.useDocuments : true);
  const [conversationId, setConversationId] = useState(() => saved.conversationId || null);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const connectingRef = useRef(false);
  const aliveRef = useRef(true);
  const reconnectTimerRef = useRef(null);
  const attemptsRef = useRef(0);
  const queueRef = useRef([]);
  

  

  useEffect(() => {
    try {
      const payload = JSON.stringify({ messages, conversationId, useDocuments });
      localStorage.setItem(STORAGE_KEY, payload);
    } catch {}
  }, [messages, conversationId, useDocuments]);

  useEffect(() => {
    if (!conversationIdProp || conversationIdProp === conversationId) return;
    (async () => {
      try {
        const res = await getConversationMessages(conversationIdProp);
        const msgs = (res.data?.messages || []).map(m => ({ role: m.role, content: m.content }));
        setConversationId(conversationIdProp);
        setMessages(msgs);
      } catch {}
    })();
  }, [conversationIdProp]);

  const ensureSocket = () => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return wsRef.current;
    }
    if (connectingRef.current) return wsRef.current;
    connectingRef.current = true;
    const socket = createChatSocket();
    wsRef.current = socket;
    socket.onopen = () => {
      connectingRef.current = false;
      console.log('WebSocket open');
      attemptsRef.current = 0;
      const q = queueRef.current;
      queueRef.current = [];
      q.forEach(msg => {
        try { socket.send(msg); } catch {}
      });
    };
    socket.onclose = (evt) => {
      // Suppress noisy close logs in dev; schedule reconnect
      connectingRef.current = false;
      if (aliveRef.current) {
        if (reconnectTimerRef.current) {
          clearTimeout(reconnectTimerRef.current);
        }
        attemptsRef.current = Math.min(attemptsRef.current + 1, 10);
        const delay = Math.min(500 * attemptsRef.current, 5000);
        reconnectTimerRef.current = setTimeout(() => {
          ensureSocket();
        }, delay);
      }
    };
    socket.onerror = (err) => {
      // Suppress noisy error logs in dev; schedule reconnect
      connectingRef.current = false;
      if (aliveRef.current) {
        if (reconnectTimerRef.current) {
          clearTimeout(reconnectTimerRef.current);
        }
        attemptsRef.current = Math.min(attemptsRef.current + 1, 10);
        const delay = Math.min(500 * attemptsRef.current, 5000);
        reconnectTimerRef.current = setTimeout(() => {
          ensureSocket();
        }, delay);
      }
    };
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'start') {
        setMessages(prev => [...prev, { role: 'assistant', content: '', sources: [] }]);
      } else if (data.type === 'token') {
        setMessages(prev => {
          const updated = [...prev];
          const cur = updated[updated.length - 1];
          const next = (cur.content || '') + (data.content || '');
          updated[updated.length - 1] = { ...cur, content: next };
          return updated;
        });
      } else if (data.type === 'end') {
        setMessages(prev => {
          const updated = [...prev];
          const cur = updated[updated.length - 1];
          const normalized = normalizeText(cur.content || '');
          updated[updated.length - 1] = { ...cur, content: normalized, sources: data.sources };
          return updated;
        });
        setIsLoading(false);
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }
      } else if (data.type === 'api_data') {
        console.log('API Data:', data.data);
      }
    };
    return socket;
  };

  const normalizeText = (t) => {
    // collapse immediate duplicate words: "Hi Hi" -> "Hi"
    let s = t.replace(/(\b[\w'’]+\b)(\s+\1\b)+/gi, '$1');
    // reduce repeated punctuation like "!!!!" -> "!"
    s = s.replace(/([!?.])\1{1,}/g, '$1');
    return s;
  };

  useEffect(() => {
    ensureSocket();
    return () => {
      try {
        const ws = wsRef.current;
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.close(1000);
        }
        wsRef.current = null;
      } catch {}
      aliveRef.current = false;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    const sock = ensureSocket();
    const payload = JSON.stringify({
        message: input,
        use_documents: useDocuments,
        tools: enabledTools,
        tool_params: toolParams,
        conversation_id: conversationId
      });
    if (sock?.readyState === WebSocket.OPEN) {
      sock.send(payload);
    } else {
      console.warn('WebSocket not open; will send after open');
      queueRef.current.push(payload);
    }

    setInput('');
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-xl">Ask me anything!</p>
            <p className="text-sm mt-2">I can search your documents and fetch live data</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${msg.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200'
                }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources?.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <FileText size={12} />
                    Sources: {msg.sources.join(', ')}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <Loader2 className="animate-spin" size={20} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="mb-4 flex items-center justify-between">
          <label className="flex items-center space-x-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={useDocuments}
              onChange={(e) => setUseDocuments(e.target.checked)}
              className="rounded"
            />
            <FileText size={16} />
            <span>Use documents</span>
          </label>
          {conversationId && (
            <button
              onClick={() => {
                setConversationId(null);
                setMessages([]);
                try { localStorage.removeItem(STORAGE_KEY); } catch {}
              }}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              + New Conversation
            </button>
          )}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
