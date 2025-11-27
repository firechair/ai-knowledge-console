import { useState } from 'react';
import { Upload, FileText, Trash2, Loader2, CheckCircle } from 'lucide-react';
import { uploadDocument, listDocuments, deleteDocument } from '../utils/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export default function DocumentUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const queryClient = useQueryClient();

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const res = await listDocuments();
      return res.data.documents;
    }
  });

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries(['documents']);
    }
  });

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus(null);

    try {
      const res = await uploadDocument(file);
      setUploadStatus({
        type: 'success',
        message: `Uploaded ${res.data.filename} (${res.data.chunks_created} chunks)`
      });
      queryClient.invalidateQueries(['documents']);
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.response?.data?.detail || 'Upload failed'
      });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Documents</h2>
      
      {/* Upload area */}
      <label className="block border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors">
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleUpload}
          className="hidden"
          disabled={uploading}
        />
        {uploading ? (
          <Loader2 className="mx-auto animate-spin text-blue-500" size={32} />
        ) : (
          <Upload className="mx-auto text-gray-400" size={32} />
        )}
        <p className="mt-2 text-gray-600">
          {uploading ? 'Processing...' : 'Click to upload PDF, DOCX, or TXT'}
        </p>
      </label>

      {/* Status message */}
      {uploadStatus && (
        <div className={`mt-4 p-3 rounded-lg ${
          uploadStatus.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {uploadStatus.type === 'success' && <CheckCircle className="inline mr-2" size={16} />}
          {uploadStatus.message}
        </div>
      )}

      {/* Document list */}
      <div className="mt-6">
        <h3 className="text-lg font-medium mb-2">Uploaded Documents</h3>
        {isLoading ? (
          <Loader2 className="animate-spin" />
        ) : documents?.length === 0 ? (
          <p className="text-gray-500">No documents uploaded yet</p>
        ) : (
          <ul className="space-y-2">
            {documents?.map((doc) => (
              <li
                key={doc}
                className="flex items-center justify-between bg-white p-3 rounded-lg border"
              >
                <span className="flex items-center gap-2">
                  <FileText size={18} className="text-blue-500" />
                  {doc}
                </span>
                <button
                  onClick={() => deleteMutation.mutate(doc)}
                  className="text-red-500 hover:text-red-700"
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 size={18} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
