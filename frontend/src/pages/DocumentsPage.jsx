import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadDocument, listDocuments, deleteDocument } from '../utils/api';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Upload, FileText, Trash2, Loader2, CheckCircle, X, File } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function DocumentsPage() {
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null);
    const [previewFile, setPreviewFile] = useState(null);
    const queryClient = useQueryClient();

    const { data: documents, isLoading } = useQuery({
        queryKey: ['documents'],
        queryFn: async () => (await listDocuments()).data.documents
    });

    const deleteMutation = useMutation({
        mutationFn: deleteDocument,
        onSuccess: () => queryClient.invalidateQueries(['documents'])
    });

    const handleFileSelect = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setUploadStatus(null);
        setPreviewFile(file);
        e.target.value = '';
    };

    const handleUpload = async () => {
        if (!previewFile) return;
        setUploading(true);
        try {
            const res = await uploadDocument(previewFile);
            setUploadStatus({ type: 'success', message: `Indexed ${res.data.filename} (${res.data.chunks_created} chunks)` });
            queryClient.invalidateQueries(['documents']);
            setPreviewFile(null);
        } catch (err) {
            setUploadStatus({ type: 'error', message: err.response?.data?.error || 'Upload failed' });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 py-6">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-2xl font-bold mb-2">Knowledge Base</h1>
                    <p className="text-[rgb(var(--text-secondary))]">Upload documents to provide context for the AI.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Upload Zone */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Add Document</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <label className="block border-2 border-dashed border-[rgb(var(--border-color))] rounded-xl p-10 text-center cursor-pointer hover:border-[rgb(var(--accent-primary))] hover:bg-[rgb(var(--accent-primary))]/5 transition-all">
                            <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileSelect} className="hidden" disabled={uploading} />
                            <div className="w-16 h-16 rounded-full bg-[rgb(var(--bg-app))] flex items-center justify-center mx-auto mb-4 border border-[rgb(var(--border-color))]">
                                {uploading ? <Loader2 className="animate-spin text-[rgb(var(--accent-primary))]" /> : <Upload className="text-[rgb(var(--text-secondary))]" />}
                            </div>
                            <p className="font-medium text-lg">Click to select a file</p>
                            <p className="text-[rgb(var(--text-secondary))] text-sm mt-1">PDF, DOCX, or TXT (Max 25MB)</p>
                        </label>

                        <AnimatePresence>
                            {previewFile && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="mt-6 p-4 rounded-lg bg-[rgb(var(--bg-app))] border border-[rgb(var(--border-color))]"
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded">
                                                <File size={20} />
                                            </div>
                                            <div>
                                                <p className="font-medium text-sm">{previewFile.name}</p>
                                                <p className="text-xs text-[rgb(var(--text-secondary))]">{(previewFile.size / 1024).toFixed(1)} KB</p>
                                            </div>
                                        </div>
                                        <Button size="icon" variant="ghost" onClick={() => setPreviewFile(null)}><X size={18} /></Button>
                                    </div>

                                    <div className="mt-4 flex gap-2 justify-end">
                                        <Button onClick={handleUpload} disabled={uploading} isLoading={uploading}>
                                            Confirm Upload
                                        </Button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {uploadStatus && (
                            <div className={cn("mt-4 p-3 rounded-lg flex items-center gap-2 text-sm", uploadStatus.type === 'success' ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400' : 'bg-red-50 text-red-700')}>
                                {uploadStatus.type === 'success' ? <CheckCircle size={16} /> : <X size={16} />}
                                {uploadStatus.message}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Existing Documents */}
                <div className="space-y-4">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-[rgb(var(--text-secondary))]">Library</h3>
                    {isLoading ? (
                        <div className="text-center py-8"><Loader2 className="animate-spin mx-auto text-[rgb(var(--text-secondary))]" /></div>
                    ) : documents?.length === 0 ? (
                        <p className="text-[rgb(var(--text-secondary))] text-sm italic">No documents indexed yet.</p>
                    ) : (
                        <ul className="space-y-2">
                            {documents?.map(doc => (
                                <motion.li
                                    key={doc}
                                    layout
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className="group flex items-center justify-between p-3 rounded-lg bg-[rgb(var(--bg-card))] border border-[rgb(var(--border-color))] hover:border-[rgb(var(--accent-primary))]/50 transition-colors"
                                >
                                    <span className="flex items-center gap-2 text-sm truncate">
                                        <FileText size={16} className="text-[rgb(var(--accent-primary))]" />
                                        <span className="truncate" title={doc}>{doc}</span>
                                    </span>
                                    <button
                                        onClick={() => deleteMutation.mutate(doc)}
                                        className="text-[rgb(var(--text-secondary))] hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </motion.li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
}
