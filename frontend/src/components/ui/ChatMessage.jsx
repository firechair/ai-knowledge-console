import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { User, Bot, FileText, ExternalLink } from 'lucide-react';
import { cn } from '../../utils/cn';

import { FileDownloadCard } from './FileDownloadCard';

export const ChatMessage = ({ role, content, sources, isStreaming }) => {
    const isUser = role === 'user';

    // Parse for file artifacts
    const fileRegex = /<file-artifact\s+filename="([^"]+)"\s+title="([^"]+)"\s+format="([^"]+)">([\s\S]*?)<\/file-artifact>/;
    const match = !isUser && content ? content.match(fileRegex) : null;

    let displayContent = content;
    let fileData = null;

    if (match) {
        displayContent = content.replace(fileRegex, '').trim();
        fileData = {
            filename: match[1],
            title: match[2],
            format: match[3],
            content: match[4].trim()
        };
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
                'flex gap-4 p-4 rounded-xl',
                isUser ? 'flex-row-reverse bg-[rgb(var(--accent-primary))]/10' : 'bg-[rgb(var(--bg-card))]/50'
            )}
        >
            <div
                className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
                    isUser ? 'bg-[rgb(var(--accent-primary))] text-white' : 'bg-emerald-500 text-white'
                )}
            >
                {isUser ? <User size={16} /> : <Bot size={16} />}
            </div>

            <div className={cn('flex-1 min-w-0 space-y-2', isUser ? 'text-right' : 'text-left')}>
                <div className="prose dark:prose-invert max-w-none text-sm leading-relaxed">
                    <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                        {displayContent}
                    </ReactMarkdown>
                </div>

                {fileData && (
                    <FileDownloadCard
                        filename={fileData.filename}
                        title={fileData.title}
                        format={fileData.format}
                        content={fileData.content}
                    />
                )}

                {sources && sources.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex flex-wrap gap-2 mt-3"
                    >
                        {sources.map((source, i) => (
                            <span
                                key={i}
                                className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-[rgb(var(--bg-app))] border border-[rgb(var(--border-color))] text-xs text-[rgb(var(--text-secondary))]"
                            >
                                <FileText size={10} />
                                {source}
                            </span>
                        ))}
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
};
