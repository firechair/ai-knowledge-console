import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Loader2, FileText, Globe, WifiOff, Wifi } from 'lucide-react';
import { createChatSocket } from '../utils/api';

export default function Chat({ enabledTools = [], toolParams = {} }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useDocuments, setUseDocuments] = useState(true);
  const [conversationId, setConversationId] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting'); // 'connecting', 'connected', 'disconnected', 'error'
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const shouldReconnectRef = useRef(true);

  const maxReconnectAttempts = 5;
  const baseDelay = 1000; // 1 second

  const handleMessage = useCallback((event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'start') {
      setMessages(prev => [...prev, { role: 'assistant', content: '', sources: [] }]);
    } else if (data.type === 'token') {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1].content += data.content;
        return updated;
      });
    } else if (data.type === 'end') {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1].sources = data.sources;
        return updated;
      });
      setIsLoading(false);
      // Update conversation ID from server
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }
    } else if (data.type === 'api_data') {
      // Could display API data in UI
      console.log('API Data:', data.data);
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    try {
      console.log('Attempting to connect WebSocket...');
      setConnectionStatus('connecting');

      const ws = createChatSocket();

      ws.onopen = () => {
        console.log('WebSocket connected successfully');
        setConnectionStatus('connected');
        reconnectAttemptRef.current = 0; // Reset reconnect attempts on successful connection
      };

      ws.onmessage = handleMessage;

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setConnectionStatus('disconnected');

        // Only attempt to reconnect if we should (not manually closed)
        if (shouldReconnectRef.current && reconnectAttemptRef.current < maxReconnectAttempts) {
          const delay = Math.min(baseDelay * Math.pow(2, reconnectAttemptRef.current), 30000);
          console.log(
            `Reconnecting in ${delay}ms... (attempt ${reconnectAttemptRef.current + 1}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptRef.current += 1;
            connectWebSocket();
          }, delay);
        } else if (reconnectAttemptRef.current >= maxReconnectAttempts) {
          console.error('Max reconnection attempts reached');
          setConnectionStatus('error');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionStatus('error');
    }
  }, [handleMessage]);

  useEffect(() => {
    shouldReconnectRef.current = true;
    connectWebSocket();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connectWebSocket]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim() || isLoading || connectionStatus !== 'connected') return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Send via WebSocket
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        message: input,
        use_documents: useDocuments,
        tools: enabledTools,
        tool_params: toolParams,
        conversation_id: conversationId
      }));
    } else {
      // WebSocket not ready, show error
      setIsLoading(false);
      console.error('WebSocket is not connected');
    }

    setInput('');
  };

  return (
    <div className="flex flex-col h-full">
      {/* Connection Status Banner */}
      {connectionStatus !== 'connected' && (
        <div
          className={`px-4 py-2 text-sm font-medium flex items-center justify-center gap-2 ${connectionStatus === 'connecting'
              ? 'bg-yellow-100 text-yellow-800'
              : connectionStatus === 'disconnected'
                ? 'bg-orange-100 text-orange-800'
                : 'bg-red-100 text-red-800'
            }`}
        >
          {connectionStatus === 'connecting' ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              <span>Connecting to chat server...</span>
            </>
          ) : connectionStatus === 'disconnected' ? (
            <>
              <WifiOff size={16} />
              <span>Reconnecting... (attempt {reconnectAttemptRef.current + 1}/{maxReconnectAttempts})</span>
            </>
          ) : (
            <>
              <WifiOff size={16} />
              <span>Connection failed. Please refresh the page.</span>
            </>
          )}
        </div>
      )}

      {connectionStatus === 'connected' && reconnectAttemptRef.current > 0 && (
        <div className="px-4 py-2 text-sm font-medium flex items-center justify-center gap-2 bg-green-100 text-green-800">
          <Wifi size={16} />
          <span>Reconnected successfully!</span>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" role="log" aria-live="polite" aria-label="Chat messages">
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
              aria-label="Use uploaded documents in responses"
            />
            <FileText size={16} />
            <span>Use documents</span>
          </label>
          {conversationId && (
            <button
              onClick={() => {
                setConversationId(null);
                setMessages([]);
              }}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              aria-label="Start new conversation"
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
            placeholder={connectionStatus === 'connected' ? "Type your message..." : "Connecting..."}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || connectionStatus !== 'connected'}
            aria-label="Chat message input"
            aria-describedby="send-button-help"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim() || connectionStatus !== 'connected'}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            title={connectionStatus !== 'connected' ? 'Waiting for connection...' : 'Send message'}
            aria-label="Send message"
            id="send-button-help"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
