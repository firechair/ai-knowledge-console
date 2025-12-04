import { useState } from 'react';
import { Upload, FileText, Trash2, Loader2, CheckCircle } from 'lucide-react';
import { uploadDocument, listDocuments, deleteDocument } from '../utils/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export default function DocumentUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [previewFile, setPreviewFile] = useState(null);
  const [previewContent, setPreviewContent] = useState('');
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

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadStatus(null);
    setPreviewFile(file);

    // Read text files for preview
    if (file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target.result;
        setPreviewContent(text.substring(0, 500) + (text.length > 500 ? '...' : ''));
      };
      reader.readAsText(file);
    } else if (file.type === 'application/pdf') {
      setPreviewContent(`📄 PDF Document\nSize: ${(file.size / 1024).toFixed(2)} KB\n\nClick "Confirm Upload" to process this PDF.`);
    } else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      setPreviewContent(`📝 Word Document\nSize: ${(file.size / 1024).toFixed(2)} KB\n\nClick "Confirm Upload" to process this document.`);
    } else {
      setPreviewContent('Preview not available for this file type.');
    }

    // Clear the input so the same file can be selected again
    e.target.value = '';
  };

  const handleConfirmUpload = async () => {
    if (!previewFile) return;

    setUploading(true);
    setUploadStatus(null);

    try {
      const res = await uploadDocument(previewFile);
      setUploadStatus({
        type: 'success',
        message: `Uploaded ${res.data.filename} (${res.data.chunks_created} chunks)`
      });
      queryClient.invalidateQueries(['documents']);
      setPreviewFile(null);
      setPreviewContent('');
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.response?.data?.error || err.response?.data?.detail || 'Upload failed'
      });
    } finally {
      setUploading(false);
    }
  };

  const handleCancelPreview = () => {
    setPreviewFile(null);
    setPreviewContent('');
    setUploadStatus(null);
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Documents</h2>

      {/* Upload area */}
      <label className="block border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors">
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
          id="file-upload"
          aria-label="Upload document file"
          aria-describedby="file-upload-help"
        />
        {uploading ? (
          <Loader2 className="mx-auto animate-spin text-blue-500" size={32} />
        ) : (
          <Upload className="mx-auto text-gray-400" size={32} />
        )}
        <p className="mt-2 text-gray-600">
          {uploading ? 'Processing...' : 'Click to upload PDF, DOCX, or TXT'}
        </p>
        <p id="file-upload-help" className="text-sm text-gray-500 mt-1">
          Supported formats: PDF, DOCX, TXT
        </p>
      </label>

      {/* Preview Panel */}
      {previewFile && !uploading && (
        <div className="mt-4 p-4 border-2 border-blue-300 rounded-lg bg-blue-50">
          <div className="flex justify-between items-start mb-3">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">{previewFile.name}</h3>
              <p className="text-sm text-gray-600">
                Size: {(previewFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
            <button
              onClick={handleCancelPreview}
              className="text-gray-500 hover:text-gray-700 px-2"
              aria-label="Cancel file selection"
            >
              ✕
            </button>
          </div>

          <div className="text-sm text-gray-700 bg-white p-3 rounded border border-gray-200 max-h-40 overflow-auto whitespace-pre-wrap font-mono text-xs">
            {previewContent}
          </div>

          <button
            onClick={handleConfirmUpload}
            className="mt-3 w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
            aria-label="Confirm and upload file"
          >
            Confirm Upload
          </button>
        </div>
      )}

      {/* Status message */}
      {uploadStatus && (
        <div className={`mt-4 p-3 rounded-lg ${uploadStatus.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
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
