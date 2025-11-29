import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, FileText, Globe } from 'lucide-react';
import { createChatSocket } from '../utils/api';

export default function Chat({ enabledTools = [], toolParams = {} }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useDocuments, setUseDocuments] = useState(true);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // Initialize WebSocket
    wsRef.current = createChatSocket();

    wsRef.current.onmessage = (event) => {
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
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket closed');
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
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

    // Send via WebSocket
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        message: input,
        use_documents: useDocuments,
        tools: enabledTools,
        tool_params: toolParams,
        conversation_id: conversationId
      }));
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
