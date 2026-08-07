import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

const statusStyles: Record<string, string> = {
  completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  active: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  online: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  error: 'bg-red-500/10 text-red-400 border-red-500/20',
  failed: 'bg-red-500/10 text-red-400 border-red-500/20',
  pending: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  processing: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  inactive: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  removed: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
};

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const style = statusStyles[status] || statusStyles.inactive;

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border font-medium capitalize',
        style,
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'
      )}
    >
      {status}
    </span>
  );
}
