import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MessageSquare, Search } from 'lucide-react';

async function fetchConversations(search = '') {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const url = new URL(`${baseUrl}/api/chat/conversations`);
    if (search) {
        url.searchParams.append('search', search);
    }

    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch conversations');
    return response.json();
}

export default function ConversationList({ onSelectConversation, selectedId }) {
    const [searchQuery, setSearchQuery] = useState('');

    const { data, isLoading } = useQuery({
        queryKey: ['conversations', searchQuery],
        queryFn: () => fetchConversations(searchQuery),
        refetchInterval: 30000, // Refetch every 30 seconds
    });

    const conversations = data?.conversations || [];

    return (
        <div className="w-72 border-r border-gray-200 bg-white flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <MessageSquare size={20} />
                    Conversations
                </h2>

                {/* Search Input */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                    <input
                        type="text"
                        placeholder="Search conversations..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        aria-label="Search conversations"
                    />
                </div>
            </div>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                    <div className="p-4 text-center text-gray-500">
                        <div className="animate-pulse">Loading...</div>
                    </div>
                ) : conversations.length === 0 ? (
                    <div className="p-4 text-center text-gray-500 text-sm">
                        {searchQuery ? 'No conversations found' : 'No conversations yet'}
                    </div>
                ) : (
                    <div className="divide-y divide-gray-100">
                        {conversations.map((conv) => (
                            <button
                                key={conv.id}
                                onClick={() => onSelectConversation(conv.id)}
                                className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${selectedId === conv.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                                    }`}
                                aria-label={`Conversation: ${conv.title}`}
                            >
                                <div className="font-medium text-sm text-gray-900 truncate mb-1">
                                    {conv.title || 'New Conversation'}
                                </div>
                                <div className="text-xs text-gray-500 truncate mb-1">
                                    {conv.preview || 'No messages yet'}
                                </div>
                                <div className="text-xs text-gray-400">
                                    {new Date(conv.created_at).toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        year: 'numeric',
                                    })}
                                </div>
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
