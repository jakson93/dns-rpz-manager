import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatsCardProps {
  icon: LucideIcon;
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  iconColor?: string;
}

export default function StatsCard({
  icon: Icon,
  title,
  value,
  change,
  changeLabel,
  iconColor = 'text-brand-400',
}: StatsCardProps) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
      <div className="flex items-center justify-between">
        <div
          className={cn(
            'flex h-12 w-12 items-center justify-center rounded-lg bg-gray-800',
            iconColor
          )}
        >
          <Icon className="h-6 w-6" />
        </div>
        {change !== undefined && (
          <div
            className={cn(
              'flex items-center gap-1 text-sm font-medium',
              change >= 0 ? 'text-emerald-400' : 'text-red-400'
            )}
          >
            {change >= 0 ? (
              <TrendingUp className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )}
            {Math.abs(change)}
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-2xl font-bold text-gray-100">{value}</h3>
        <p className="mt-1 text-sm text-gray-400">{title}</p>
        {changeLabel && (
          <p className="text-xs text-gray-500 mt-1">{changeLabel}</p>
        )}
      </div>
    </div>
  );
}
