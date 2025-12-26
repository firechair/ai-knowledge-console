import { NavLink, useLocation, Link } from 'react-router-dom';
import { MessageSquare, FileText, Plug, Settings, List, Box, Sun, Moon } from 'lucide-react';
import { cn } from '../../utils/cn';
import { useTheme } from '../../hooks/useTheme';
import { Button } from '../ui/Button';

export function Sidebar() {
    const location = useLocation();
    const { theme, toggleTheme } = useTheme();
    const isOnConversation = location.pathname.startsWith('/chat/');

    // Get last conversation from localStorage to restore when navigating back
    const getLastConversationPath = () => {
        if (isOnConversation) {
            return location.pathname; // Stay on current conversation
        }
        const lastConversationId = localStorage.getItem('lastConversationId');
        return lastConversationId ? `/chat/${lastConversationId}` : '/';
    };

    const navItems = [
        {
            path: getLastConversationPath(),
            label: 'Chat',
            icon: MessageSquare
        },
        { path: '/conversations', label: 'Conversations', icon: List },
        { path: '/documents', label: 'Knowledge Base', icon: FileText },
        { path: '/connectors', label: 'Connectors', icon: Plug },
        { path: '/settings', label: 'Settings', icon: Settings },
    ];
    return (
        <aside className="w-64 border-r border-[rgb(var(--border-color))] bg-[rgb(var(--bg-app))]/50 backdrop-blur-sm hidden md:flex flex-col">
            <Link to="/" className="p-6 flex items-center gap-3 hover:opacity-80 transition-opacity">
                <div className="w-8 h-8 rounded-lg bg-[rgb(var(--accent-primary))] flex items-center justify-center text-white shadow-lg shadow-[rgb(var(--accent-primary))]/30">
                    <Box size={20} />
                </div>
                <span className="font-bold text-lg tracking-tight">AI Console</span>
            </Link>

            <nav className="flex-1 px-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            cn(
                                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                                isActive
                                    ? 'bg-[rgb(var(--accent-primary))]/10 text-[rgb(var(--accent-primary))]'
                                    : 'text-[rgb(var(--text-secondary))] hover:bg-[rgb(var(--text-secondary))]/10 hover:text-[rgb(var(--text-primary))]'
                            )
                        }
                    >
                        {({ isActive }) => (
                            <>
                                <item.icon size={18} className={cn(isActive ? 'text-[rgb(var(--accent-primary))]' : 'opacity-70')} />
                                {item.label}
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-[rgb(var(--border-color))]">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 px-3 py-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500" />
                        <div className="flex flex-col text-left">
                            <span className="text-sm font-medium">User</span>
                            <span className="text-xs text-[rgb(var(--text-secondary))]">Pro Plan</span>
                        </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={toggleTheme} className="hover:bg-[rgb(var(--accent-primary))]/10">
                        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
                    </Button>
                </div>
            </div>
        </aside>
    );
}
