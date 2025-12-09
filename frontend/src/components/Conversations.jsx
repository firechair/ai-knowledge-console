import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listConversations, deleteConversation, createConversation, deleteAllConversations, renameConversation } from '../utils/api';
import { Trash2, FolderPlus, RefreshCw } from 'lucide-react';

export default function Conversations({ onSelectConversation }) {
  const queryClient = useQueryClient();
  const [editingId, setEditingId] = useState(null);
  const [titleInput, setTitleInput] = useState('');

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const res = await listConversations();
      return res.data.conversations || [];
    }
  });

  const delMutation = useMutation({
    mutationFn: (id) => deleteConversation(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['conversations']);
    }
  });

  const createMutation = useMutation({
    mutationFn: createConversation,
    onSuccess: (res) => {
      queryClient.invalidateQueries(['conversations']);
      const id = res.data?.id;
      if (id) onSelectConversation?.(id);
    }
  });

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Conversations</h2>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded">
            <RefreshCw size={16} />
          </button>
          <button onClick={() => {
            if (confirm('Delete ALL conversations? This cannot be undone.')) {
              deleteAllConversations().then(() => queryClient.invalidateQueries(['conversations']));
            }
          }} className="px-3 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700">
            <Trash2 size={16} /> Delete All
          </button>
          <button onClick={() => createMutation.mutate()} className="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
            <FolderPlus size={16} /> New
          </button>
        </div>
      </div>

      {isLoading && <p className="text-gray-500">Loading conversations...</p>}
      {isError && <p className="text-red-600">Failed to load conversations</p>}

      {!isLoading && (data?.length === 0) && (
        <div className="bg-white border rounded p-6 text-center text-gray-600">
          No conversations yet. Create a new one or start chatting.
        </div>
      )}

      <div className="space-y-3">
        {data?.map((c) => (
          <div key={c.id} className="bg-white border rounded-lg p-4 flex items-center justify-between">
            <div>
              {editingId === c.id ? (
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={titleInput}
                    onChange={(e) => setTitleInput(e.target.value)}
                    placeholder="Conversation title"
                    className="border rounded px-2 py-1 text-sm"
                  />
                  <button
                    onClick={async () => {
                      const t = titleInput.trim();
                      if (t) {
                        await renameConversation(c.id, t);
                        setEditingId(null);
                        setTitleInput('');
                        queryClient.invalidateQueries(['conversations']);
                      }
                    }}
                    className="px-2 py-1 text-sm bg-blue-600 text-white rounded"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => { setEditingId(null); setTitleInput(''); }}
                    className="px-2 py-1 text-sm text-gray-600"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <p className="font-medium">{c.title || c.id}</p>
              )}
              <p className="text-sm text-gray-500">Created: {new Date(c.created_at).toLocaleString()}</p>
              {c.last_message_preview && (
                <p className="text-sm text-gray-600 mt-1">{c.last_message_preview}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {editingId !== c.id && (
                <button
                  onClick={() => { setEditingId(c.id); setTitleInput(c.title || ''); }}
                  className="px-3 py-1 rounded text-sm bg-gray-100 text-gray-700 hover:bg-gray-200"
                >
                  Rename
                </button>
              )}
              <button onClick={() => onSelectConversation?.(c.id)} className="px-3 py-1 rounded text-sm bg-blue-600 text-white hover:bg-blue-700">
                Open
              </button>
              <button onClick={() => {
                if (confirm('Delete this conversation? This cannot be undone.')) {
                  delMutation.mutate(c.id);
                }
              }} className="px-3 py-1 rounded text-sm bg-red-100 text-red-700 hover:bg-red-200">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
