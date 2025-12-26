import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listConnectors, configureConnector, toggleConnector, API_BASE } from '../utils/api';
import { Card, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Github, Cloud, Bitcoin, Newspaper, Check, X, Settings, Mail, File, Slack, Book, Lock } from 'lucide-react';
import { cn } from '../utils/cn';

const CONNECTOR_INFO = {
    // Category: Integrations (OAuth-based)
    gmail: { icon: Mail, name: 'Gmail', oauth: true, category: 'integrations', description: 'Search emails and threads' },
    drive: { icon: File, name: 'Google Drive', oauth: true, category: 'integrations', description: 'Access document contents' },
    slack: { icon: Slack, name: 'Slack', oauth: true, category: 'integrations', description: 'Search channel history' },
    notion: { icon: Book, name: 'Notion', oauth: true, category: 'integrations', description: 'Retrieve page content' },

    // Category: API Services (API keys + public)
    github: { icon: Github, name: 'GitHub', needsKey: true, category: 'services', description: 'Search commits and repositories' },
    weather: { icon: Cloud, name: 'Weather', needsKey: true, category: 'services', description: 'Live weather updates' },
    crypto: { icon: Bitcoin, name: 'Crypto', needsKey: false, category: 'services', description: 'Real-time cryptocurrency prices' },
    hackernews: { icon: Newspaper, name: 'Hacker News', needsKey: false, category: 'services', description: 'Top tech news stories' }
};

export default function ConnectorsPage() {
    const [configuring, setConfiguring] = useState(null);
    const [apiKey, setApiKey] = useState('');
    const queryClient = useQueryClient();

    const { data: connectors, isLoading } = useQuery({
        queryKey: ['connectors'],
        queryFn: async () => {
            const res = await listConnectors();
            return res.data.connectors;
        }
    });

    const toggleMutation = useMutation({
        mutationFn: toggleConnector,
        onSuccess: () => queryClient.invalidateQueries(['connectors'])
    });

    const configureMutation = useMutation({
        mutationFn: configureConnector,
        onSuccess: () => {
            queryClient.invalidateQueries(['connectors']);
            setConfiguring(null);
            setApiKey('');
        }
    });

    const handleOAuth = (name) => {
        const returnUrl = `${window.location.origin}/connectors`;
        const state = encodeURIComponent(JSON.stringify({ return_url: returnUrl }));
        const provider = (name === 'gmail' || name === 'drive') ? 'google' : name;

        // Determine API Base
        const apiBase = API_BASE || window.location.origin.replace('5173', '8000');
        const cleanBase = apiBase.replace(/\/$/, '') + (apiBase.includes('/api') ? '' : '/api');

        window.location.href = `${cleanBase}/auth/${provider}/login?state=${state}`;
    };

    if (isLoading) {
        return <div className="p-12 text-center text-[rgb(var(--text-secondary))]">Loading connectors...</div>;
    }

    const renderConnectorCard = (name, status) => {
        const info = CONNECTOR_INFO[name] || { name, icon: Settings, description: 'Custom connector', category: 'services' };
        const Icon = info.icon;

        return (
            <Card key={name} className="flex flex-col h-full border-[rgb(var(--border-color))] shadow-sm hover:shadow-md transition-all">
                <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
                    <div className="p-2 rounded-lg bg-[rgb(var(--text-secondary))]/10">
                        <Icon size={24} className="text-[rgb(var(--text-primary))]" />
                    </div>
                    <div className="flex items-center gap-2">
                        {status.configured && <Check size={16} className="text-green-500" />}
                    </div>
                </CardHeader>
                <div className="px-6 flex-1">
                    <h3 className="font-semibold text-lg">{info.name}</h3>
                    <p className="text-sm text-[rgb(var(--text-secondary))] mt-1">{info.description}</p>
                </div>

                <div className="p-6 pt-4 mt-auto space-y-4">
                    {/* Configuration Area */}
                    {configuring === name ? (
                        <div className="space-y-2 animate-in slide-in-from-top-2 fade-in">
                            <Input
                                type="password"
                                placeholder="Enter API Key"
                                value={apiKey}
                                onChange={e => setApiKey(e.target.value)}
                                autoFocus
                            />
                            <div className="flex gap-2">
                                <Button size="sm" onClick={() => configureMutation.mutate({ name, api_key: apiKey })}>Save</Button>
                                <Button size="sm" variant="ghost" onClick={() => setConfiguring(null)}>Cancel</Button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex gap-2">
                            {/* Configure / Auth Button - Only show for OAuth or connectors that need keys */}
                            {info.oauth ? (
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    className="flex-1"
                                    disabled={status.configured}
                                    onClick={() => handleOAuth(name)}
                                >
                                    {status.configured ? 'Authorized' : 'Connect'}
                                </Button>
                            ) : info.needsKey ? (
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    className="flex-1"
                                    onClick={() => setConfiguring(name)}
                                >
                                    <Settings size={14} className="mr-2" />
                                    Configure
                                </Button>
                            ) : null}

                            {/* Toggle Button */}
                            <Button
                                variant={status.enabled ? 'primary' : 'ghost'}
                                size="sm"
                                disabled={!status.configured}
                                onClick={() => toggleMutation.mutate(name)}
                                className={cn(!status.enabled && 'bg-gray-100 dark:bg-zinc-800', !info.oauth && !info.needsKey && 'flex-1')}
                            >
                                {status.enabled ? 'On' : 'Off'}
                            </Button>
                        </div>
                    )}
                </div>
            </Card>
        );
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 py-6">
            <div>
                <h1 className="text-2xl font-bold mb-2">Connectors</h1>
                <p className="text-[rgb(var(--text-secondary))]">Manage integrations with external tools and services.</p>
            </div>

            {/* Integrations Section */}
            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-[rgb(var(--text-primary))]">Integrations</h2>
                    <p className="text-sm text-[rgb(var(--text-secondary))] mt-1">
                        OAuth-based connections requiring authorization
                    </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {connectors && Object.entries(connectors)
                        .filter(([name]) => CONNECTOR_INFO[name]?.category === 'integrations')
                        .map(([name, status]) => renderConnectorCard(name, status))}
                </div>
            </section>

            {/* API Services Section */}
            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-[rgb(var(--text-primary))]">API Services</h2>
                    <p className="text-sm text-[rgb(var(--text-secondary))] mt-1">
                        Data sources and tools with API key or public access
                    </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {connectors && Object.entries(connectors)
                        .filter(([name]) => CONNECTOR_INFO[name]?.category === 'services')
                        .map(([name, status]) => renderConnectorCard(name, status))}
                </div>
            </section>
        </div>
    );
}
