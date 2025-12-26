import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listConversations, deleteConversation, createConversation, deleteAllConversations, renameConversation } from '../utils/api';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Trash2, Plus, MessageSquare, Clock, Edit2, Archive } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ConversationsPage() {
    const queryClient = useQueryClient();
    const navigate = useNavigate();
    const [editingId, setEditingId] = useState(null);
    const [titleInput, setTitleInput] = useState('');

    const { data: conversations, isLoading } = useQuery({
        queryKey: ['conversations'],
        queryFn: async () => (await listConversations()).data.conversations || []
    });

    const createMutation = useMutation({
        mutationFn: createConversation,
        onSuccess: (res) => {
            queryClient.invalidateQueries(['conversations']);
            if (res.data?.id) navigate(`/chat/${res.data.id}`);
        }
    });

    const deleteMutation = useMutation({
        mutationFn: deleteConversation,
        onSuccess: () => queryClient.invalidateQueries(['conversations'])
    });

    const renameMutation = useMutation({
        mutationFn: ({ id, title }) => renameConversation(id, title),
        onSuccess: () => {
            queryClient.invalidateQueries(['conversations']);
            setEditingId(null);
        }
    });

    const handleOpen = (id) => {
        // Navigate to chat with conversation ID in URL
        navigate(`/chat/${id}`);
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 py-6">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold mb-2">Conversations</h1>
                    <p className="text-[rgb(var(--text-secondary))]">Manage your chat history and sessions.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="ghost" onClick={() => {
                        if (confirm('Delete all history?')) deleteAllConversations().then(() => queryClient.invalidateQueries(['conversations']));
                    }}>
                        <Archive size={16} className="mr-2" /> Clear All
                    </Button>
                    <Button onClick={() => createMutation.mutate()}>
                        <Plus size={16} className="mr-2" /> New Chat
                    </Button>
                </div>
            </div>

            {isLoading ? (
                <div className="p-12 text-center text-[rgb(var(--text-secondary))]">Loading history...</div>
            ) : conversations?.length === 0 ? (
                <Card className="p-12 text-center flex flex-col items-center">
                    <div className="w-16 h-16 bg-gray-100 dark:bg-zinc-800 rounded-full flex items-center justify-center mb-4">
                        <MessageSquare size={24} className="text-[rgb(var(--text-secondary))]" />
                    </div>
                    <h3 className="text-lg font-medium">No conversations found</h3>
                    <p className="text-[rgb(var(--text-secondary))] mt-2 mb-6">Start a new chat to see it appear here.</p>
                    <Button onClick={() => createMutation.mutate()}>Start Chatting</Button>
                </Card>
            ) : (
                <div className="flex flex-col gap-4">
                    <AnimatePresence>
                        {conversations?.map((c) => (
                            <motion.div
                                key={c.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, height: 0 }}
                                layout
                                className="group w-full min-w-0"
                            >
                                <Card className="flex flex-col md:flex-row md:items-center justify-between gap-4 py-4 px-6 hover:border-[rgb(var(--accent-primary))]/50 transition-colors cursor-pointer" onClick={(e) => {
                                    if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'SVG' && e.target.tagName !== 'PATH') {
                                        handleOpen(c.id);
                                    }
                                }}>
                                    <div className="flex-1 min-w-0">
                                        {editingId === c.id ? (
                                            <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                                                <Input
                                                    autoFocus
                                                    value={titleInput}
                                                    onChange={e => setTitleInput(e.target.value)}
                                                    onKeyDown={e => {
                                                        if (e.key === 'Enter') renameMutation.mutate({ id: c.id, title: titleInput });
                                                        if (e.key === 'Escape') setEditingId(null);
                                                    }}
                                                    className="max-w-md h-8"
                                                />
                                                <Button size="sm" onClick={() => renameMutation.mutate({ id: c.id, title: titleInput })}>Save</Button>
                                                <Button size="sm" variant="ghost" onClick={() => setEditingId(null)}>Cancel</Button>
                                            </div>
                                        ) : (
                                            <div className="group/title flex items-center gap-2">
                                                <h3 className="font-semibold text-lg truncate min-w-0 group-hover:text-[rgb(var(--accent-primary))] transition-colors duration-200">
                                                    {c.title || 'Untitled Conversation'}
                                                </h3>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); setEditingId(c.id); setTitleInput(c.title || ''); }}
                                                    className="opacity-0 group-hover/title:opacity-100 text-[rgb(var(--text-secondary))] hover:text-[rgb(var(--text-primary))]"
                                                >
                                                    <Edit2 size={14} />
                                                </button>
                                            </div>
                                        )}

                                        <div className="flex items-center gap-4 mt-1 text-xs text-[rgb(var(--text-secondary))]">
                                            <span className="flex items-center gap-1 shrink-0">
                                                <Clock size={12} />
                                                {new Date(c.created_at).toLocaleDateString()}
                                            </span>
                                            <span className="truncate min-w-0 flex-1 opacity-70">
                                                {c.last_message_preview || 'No messages yet'}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                                        <Button size="sm" variant="secondary" onClick={() => handleOpen(c.id)}>Open</Button>
                                        <Button size="sm" variant="ghost" className="text-red-500 hover:text-red-700 hover:bg-red-50" onClick={() => {
                                            if (confirm('Delete conversation?')) deleteMutation.mutate(c.id);
                                        }}>
                                            <Trash2 size={18} />
                                        </Button>
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            )}
        </div>
    );
}
