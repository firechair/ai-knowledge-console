import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { setEmbeddingModel } from '../utils/api';

export default function Settings() {
  const [modelName, setModelName] = useState('all-MiniLM-L6-v2');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const updateModel = async () => {
    setLoading(true);
    setStatus('');
    try {
      await setEmbeddingModel(modelName);
      setStatus(`Embedding model set to ${modelName}`);
    } catch (e) {
      setStatus(`Error: ${e?.response?.data?.detail || e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-lg font-semibold mb-4">Settings</h2>
      <div className="bg-white rounded-lg shadow p-4 max-w-md">
        <label className="block text-sm font-medium mb-2">Embedding Model</label>
        <input
          type="text"
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-3"
          placeholder="e.g. all-MiniLM-L6-v2"
        />
        <button
          onClick={updateModel}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50 flex items-center gap-2"
        >
          {loading && <Loader2 className="animate-spin" size={16} />}
          Apply
        </button>
        {status && (
          <p className="text-sm text-gray-600 mt-3">{status}</p>
        )}
      </div>
    </div>
  );
}

