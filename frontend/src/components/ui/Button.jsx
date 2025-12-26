import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

const variants = {
    primary: 'bg-[rgb(var(--accent-primary))] text-white hover:opacity-90 shadow-lg shadow-[rgb(var(--accent-glow))]/20',
    secondary: 'bg-[rgb(var(--bg-card))] text-[rgb(var(--text-primary))] border border-[rgb(var(--border-color))] hover:bg-gray-50 dark:hover:bg-zinc-800',
    ghost: 'text-[rgb(var(--text-secondary))] hover:text-[rgb(var(--text-primary))] hover:bg-gray-100/50 dark:hover:bg-zinc-800/50',
    desctructive: 'bg-red-500 text-white hover:bg-red-600',
};

const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
    icon: 'p-2',
};

export const Button = ({
    children,
    variant = 'primary',
    size = 'md',
    className,
    isLoading,
    ...props
}) => {
    return (
        <motion.button
            whileTap={{ scale: 0.98 }}
            className={cn(
                'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[rgb(var(--accent-primary))]/50 disabled:opacity-50 disabled:pointer-events-none',
                variants[variant],
                sizes[size],
                className
            )}
            disabled={isLoading}
            {...props}
        >
            {isLoading && (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            )}
            {children}
        </motion.button>
    );
};
