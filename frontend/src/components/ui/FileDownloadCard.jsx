import { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { FileText, Download, Loader2, Check, AlertTriangle, File } from 'lucide-react';
import { API_BASE } from '../../utils/api';

export function FileDownloadCard({ filename, title, content, format }) {
    const [status, setStatus] = useState('idle'); // idle, generating, completed, error
    const [downloadUrl, setDownloadUrl] = useState(null);

    const handleDownload = async () => {
        setStatus('generating');
        try {
            const res = await fetch(`${API_BASE}/api/files/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content,
                    filename,
                    title,
                    format
                })
            });

            if (!res.ok) throw new Error('Generation failed');

            const data = await res.json();
            const dlUrl = data.download_url || data.url;
            setDownloadUrl(dlUrl);

            // Prefer downloading via blob to ensure attachment behavior across origins
            try {
                const dlRes = await fetch(dlUrl, { method: 'GET' });
                if (!dlRes.ok) throw new Error('Download failed');
                const blob = await dlRes.blob();
                const objectUrl = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = objectUrl;
                link.download = data.filename || filename || 'download';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(objectUrl);
                setStatus('completed');
            } catch (e) {
                // Fallback to direct link if blob fails
                const link = document.createElement('a');
                link.href = dlUrl;
                link.download = data.filename || filename || 'download';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                setStatus('completed');
            }

        } catch (error) {
            console.error(error);
            setStatus('error');
        }
    };

    return (
        <Card className="my-4 p-4 border-[rgb(var(--accent-primary))]/20 bg-[rgb(var(--accent-primary))]/5 max-w-md">
            <div className="flex items-start gap-4">
                <div className="p-3 bg-white dark:bg-zinc-800 rounded-xl shadow-sm border border-[rgb(var(--border-color))] text-[rgb(var(--accent-primary))]">
                    <FileText size={24} />
                </div>
                <div className="flex-1">
                    <h4 className="font-semibold text-sm text-[rgb(var(--text-primary))]">{title || filename}</h4>
                    <p className="text-xs text-[rgb(var(--text-secondary))] mb-3">
                        {format.toUpperCase()} Document • Ready to generate
                    </p>

                    <div className="flex items-center gap-2">
                        {status === 'idle' && (
                            <Button size="sm" onClick={handleDownload} className="w-full sm:w-auto">
                                <Download size={14} className="mr-2" />
                                Generate & Download
                            </Button>
                        )}
                        {status === 'generating' && (
                            <Button size="sm" disabled className="w-full sm:w-auto opacity-80">
                                <Loader2 size={14} className="mr-2 animate-spin" />
                                Generating...
                            </Button>
                        )}
                        {status === 'completed' && (
                            <a
                                href={downloadUrl}
                                download
                                className="inline-flex items-center justify-center px-3 py-1.5 text-xs rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[rgb(var(--accent-primary))]/50 text-green-600 bg-green-50 dark:bg-green-900/20 ring-1 ring-green-500/20 w-full sm:w-auto"
                            >
                                <Check size={14} className="mr-2" />
                                Downloaded
                            </a>
                        )}
                        {status === 'error' && (
                            <div className="flex items-center gap-2 text-red-500 text-xs">
                                <AlertTriangle size={14} />
                                <span>Failed to generate</span>
                                <button onClick={handleDownload} className="underline hover:text-red-600">Retry</button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </Card>
    );
}
