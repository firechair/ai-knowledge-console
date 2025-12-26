import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

export const Card = ({ children, className, ...props }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={cn(
                'glass-card rounded-xl p-6',
                className
            )}
            {...props}
        >
            {children}
        </motion.div>
    );
};

export const CardHeader = ({ children, className }) => (
    <div className={cn('mb-4', className)}>{children}</div>
);

export const CardTitle = ({ children, className }) => (
    <h3 className={cn('text-lg font-semibold text-[rgb(var(--text-primary))]', className)}>
        {children}
    </h3>
);

export const CardDescription = ({ children, className }) => (
    <p className={cn('text-sm text-[rgb(var(--text-secondary))] mt-1', className)}>
        {children}
    </p>
);

export const CardContent = ({ children, className }) => (
    <div className={cn('', className)}>{children}</div>
);
