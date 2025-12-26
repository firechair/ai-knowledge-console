import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Loader2, Download, Check, AlertTriangle, HardDrive } from 'lucide-react';

export function ModelManager() {
  const [llmModels, setLlmModels] = useState([]);
  const [embeddingModels, setEmbeddingModels] = useState([]);
  const [downloads, setDownloads] = useState({});
  const [loading, setLoading] = useState(false);

  // LLM Download Form
  const [llmRepo, setLlmRepo] = useState('');
  const [llmFilename, setLlmFilename] = useState('');
  const [hfToken, setHfToken] = useState('');

  // Embedding Download Form
  const [embeddingModel, setEmbeddingModel] = useState('all-MiniLM-L6-v2');
  const [activeModel, setActiveModel] = useState('');

  useEffect(() => {
    loadModels();
    const interval = setInterval(checkDownloads, 2000);
    return () => clearInterval(interval);
  }, []);

  const loadModels = async () => {
    try {
      const [llm, embedding] = await Promise.all([
        fetch('/api/models/llm').then(r => r.json()),
        fetch('/api/models/embedding').then(r => r.json())
      ]);
      setLlmModels(llm.models || []);
      setEmbeddingModels(embedding.models || []);
      if (embedding.active_model) {
        setActiveModel(embedding.active_model);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const activateEmbeddingModel = async (modelName) => {
    try {
      const res = await fetch('/api/settings/embedding_model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: modelName })
      });
      if (res.ok) {
        setActiveModel(modelName);
      }
    } catch (e) {
      console.error("Failed to set active model", e);
    }
  };

  const checkDownloads = async () => {
    try {
      const response = await fetch('/api/models/downloads');
      const data = await response.json();
      setDownloads(data.downloads || {});
    } catch (error) {
      console.error('Failed to check downloads:', error);
    }
  };

  const downloadLLMModel = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/models/llm/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_id: llmRepo,
          filename: llmFilename,
          token: hfToken
        })
      });
      if (!response.ok) throw new Error('Download failed');
      alert('Download started! Check progress below.');
      setLlmRepo('');
      setLlmFilename('');
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadEmbeddingModel = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/models/embedding/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_name: embeddingModel })
      });
      if (!response.ok) throw new Error('Download failed');
      alert('Download started!');
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* LLM Models Section */}
      <Card>
        <CardHeader>
          <CardTitle>LLM Models (GGUF)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Local Models List */}
          <div>
            <h3 className="text-sm font-semibold mb-3">Local Models</h3>
            {llmModels.length === 0 ? (
              <p className="text-sm text-gray-600 dark:text-gray-400">No local models found in backend/models/</p>
            ) : (
              <div className="space-y-2">
                {llmModels.map(model => (
                  <div key={model.filename} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium text-sm">{model.filename}</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">{model.size_mb} MB</div>
                    </div>
                    <HardDrive size={16} className="text-green-600" />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Download Form */}
          <div className="space-y-4 pt-4 border-t">
            <h3 className="text-sm font-semibold">Download from HuggingFace</h3>
            <Input
              label="Repository ID"
              placeholder="TheBloke/Llama-2-7B-Chat-GGUF"
              value={llmRepo}
              onChange={e => setLlmRepo(e.target.value)}
            />
            <Input
              label="Filename"
              placeholder="llama-2-7b-chat.Q4_K_M.gguf"
              value={llmFilename}
              onChange={e => setLlmFilename(e.target.value)}
            />
            <Input
              label="HuggingFace Token (optional)"
              type="password"
              placeholder="hf_..."
              value={hfToken}
              onChange={e => setHfToken(e.target.value)}
            />
            <Button
              onClick={downloadLLMModel}
              disabled={!llmRepo || !llmFilename || loading}
              className="w-full"
            >
              {loading ? <Loader2 size={16} className="mr-2 animate-spin" /> : <Download size={16} className="mr-2" />}
              Download Model
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Embedding Models Section */}
      <Card>
        <CardHeader>
          <CardTitle>Embedding Models</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Local Models */}
          <div>
            <h3 className="text-sm font-semibold mb-3">Available Local Models</h3>
            {embeddingModels.length === 0 ? (
              <p className="text-sm text-gray-600 dark:text-gray-400">No cached models found</p>
            ) : (
              <div className="space-y-2">
                {embeddingModels.map(model => (
                  <div key={model} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <input
                        type="radio"
                        name="activeModel"
                        checked={activeModel === model}
                        onChange={() => activateEmbeddingModel(model)}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-sm font-mono">{model}</span>
                    </div>
                    {activeModel === model && <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Active</span>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Download Form */}
          <div className="space-y-4 pt-4 border-t">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold">Download from HuggingFace</h3>
              <span className="text-[10px] text-gray-500 bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                Sentence-Transformers Hub
              </span>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-500 font-medium">Quick Select Popular Models</label>
              <select
                value={embeddingModels.includes(embeddingModel) ? embeddingModel : ""}
                onChange={e => setEmbeddingModel(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg text-sm bg-white dark:bg-gray-900"
              >
                <option value="" disabled>-- Choose a model to auto-fill below --</option>
                <optgroup label="General Purpose">
                  <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (Default, balanced)</option>
                  <option value="all-mpnet-base-v2">all-mpnet-base-v2 (Higher accuracy)</option>
                  <option value="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2">multilingual-MiniLM-L12 (Multi-language)</option>
                </optgroup>
                <optgroup label="High Performance / Large">
                  <option value="BAAI/bge-m3">BAAI/bge-m3 (SOTA Multilingual)</option>
                  <option value="mixedbread-ai/mxbai-embed-large-v1">mxbai-embed-large-v1 (SOTA English)</option>
                  <option value="nomic-ai/nomic-embed-text-v1.5">nomic-embed-text-v1.5 (Long context)</option>
                </optgroup>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-gray-500 font-medium">Model ID / Custom</label>
              <Input
                placeholder="e.g. sentence-transformers/all-MiniLM-L6-v2"
                value={embeddingModel}
                onChange={e => setEmbeddingModel(e.target.value)}
              />
              <p className="text-[10px] text-gray-400 italic">
                You can enter any model ID from HuggingFace that is compatible with Sentence-Transformers.
              </p>
            </div>
            <Button onClick={downloadEmbeddingModel} disabled={!embeddingModel || loading} className="w-full">
              {loading ? <Loader2 size={16} className="mr-2 animate-spin" /> : <Download size={16} className="mr-2" />}
              Download Model
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Downloads Progress */}
      {Object.keys(downloads).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Download Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(downloads).map(([id, status]) => (
                <div key={id} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium truncate flex-1">{id}</span>
                    {status.status === 'completed' && <Check size={16} className="text-green-600 ml-2" />}
                    {status.status === 'downloading' && <Loader2 size={16} className="animate-spin ml-2" />}
                    {status.status === 'error' && <AlertTriangle size={16} className="text-red-600 ml-2" />}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Status: {status.status}
                    {status.error && ` - ${status.error}`}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
