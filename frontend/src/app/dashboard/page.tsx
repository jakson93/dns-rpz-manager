'use client';

import { useQuery } from '@tanstack/react-query';
import {
  Shield,
  Globe,
  Upload,
  Server,
  TrendingUp,
  TrendingDown,
  Clock,
  AlertCircle,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import api from '@/lib/api';
import StatsCard from '@/components/StatsCard';
import StatusBadge from '@/components/StatusBadge';
import DataTable, { Column } from '@/components/DataTable';
import { DashboardStats, RecentImport, DailyStat } from '@/types';
import { format } from 'date-fns';

interface DashboardResponse {
  stats: DashboardStats;
  recent_imports: RecentImport[];
  daily_stats: DailyStat[];
}

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery<DashboardResponse>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const [statsRes, importsRes] = await Promise.all([
        api.get('/v1/dashboard/stats'),
        api.get('/v1/dashboard/recent-imports'),
      ]);
      return {
        stats: statsRes.data,
        recent_imports: importsRes.data?.items || importsRes.data || [],
        daily_stats: statsRes.data?.daily_stats || [],
      };
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-200">Failed to load dashboard</h3>
        <p className="text-sm text-gray-500 mt-1">Please check your connection and try again.</p>
      </div>
    );
  }

  const stats = data?.stats;
  const recentImports = data?.recent_imports || [];
  const dailyStats = data?.daily_stats || [];

  const importColumns: Column<RecentImport>[] = [
    {
      key: 'filename',
      header: 'File',
      render: (item) => (
        <span className="font-medium text-gray-200">{item.filename}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => <StatusBadge status={item.status} size="sm" />,
    },
    {
      key: 'domains_added',
      header: 'Added',
      render: (item) => (
        <span className="text-emerald-400">+{item.domains_added}</span>
      ),
    },
    {
      key: 'domains_removed',
      header: 'Removed',
      render: (item) => (
        <span className="text-red-400">-{item.domains_removed}</span>
      ),
    },
    {
      key: 'created_at',
      header: 'Date',
      render: (item) => (
        <span className="text-gray-400">
          {format(new Date(item.created_at), 'MMM d, yyyy HH:mm')}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          icon={Shield}
          title="Total Blocked Domains"
          value={stats?.total_blocked_domains || 0}
          change={stats?.domains_added_this_week}
          changeLabel="this week"
          iconColor="text-red-400"
        />
        <StatsCard
          icon={Globe}
          title="Active Domains"
          value={stats?.active_domains || 0}
          change={stats?.domains_added_this_week}
          changeLabel="added this week"
          iconColor="text-emerald-400"
        />
        <StatsCard
          icon={Server}
          title="DNS Servers Online"
          value={`${stats?.dns_servers_online || 0}/${stats?.dns_servers_total || 0}`}
          iconColor="text-blue-400"
        />
        <StatsCard
          icon={Upload}
          title="Total Imports"
          value={stats?.total_imports || 0}
          iconColor="text-purple-400"
        />
      </div>

      {dailyStats.length > 0 && (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <h3 className="mb-4 text-lg font-semibold text-gray-100">
            Domains Added/Removed Over Time
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis
                  dataKey="date"
                  stroke="#6b7280"
                  fontSize={12}
                  tickFormatter={(value) =>
                    format(new Date(value), 'MMM d')
                  }
                />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f3f4f6',
                  }}
                  labelFormatter={(value) =>
                    format(new Date(value), 'MMM d, yyyy')
                  }
                />
                <Legend />
                <Bar
                  dataKey="added"
                  name="Added"
                  fill="#10b981"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="removed"
                  name="Removed"
                  fill="#ef4444"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div>
        <h3 className="mb-4 text-lg font-semibold text-gray-100">
          Recent Imports
        </h3>
        <DataTable
          columns={importColumns}
          data={recentImports}
          keyExtractor={(item) => item.id}
          emptyMessage="No recent imports"
        />
      </div>
    </div>
  );
}
