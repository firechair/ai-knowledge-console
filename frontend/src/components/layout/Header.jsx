import { useTheme } from '../../hooks/useTheme';
import { Sun, Moon, Bell } from 'lucide-react';
import { Button } from '../ui/Button';

export function Header() {
    return (
        <header className="h-16 border-b border-[rgb(var(--border-color))] glass flex items-center justify-end px-6 sticky top-0 z-10">
            <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon">
                    <Bell size={20} />
                </Button>
            </div>
        </header>
    );
}
