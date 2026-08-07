'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { AlertCircle } from 'lucide-react';
import api from '@/lib/api';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import { ImportJob } from '@/types';

interface HistoryResponse {
  items: ImportJob[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export default function HistoryPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery<HistoryResponse>({
    queryKey: ['history', page],
    queryFn: async () => {
      const response = await api.get('/v1/import/history', {
        params: { page, per_page: 10 },
      });
      return response.data;
    },
  });

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-200">
          Failed to load history
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Please check your connection and try again.
        </p>
      </div>
    );
  }

  const columns: Column<ImportJob>[] = [
    {
      key: 'filename',
      header: 'Filename',
      sortable: true,
      render: (item) => (
        <span className="font-medium text-gray-200">{item.filename}</span>
      ),
    },
    {
      key: 'created_at',
      header: 'Date',
      sortable: true,
      render: (item) => (
        <span className="text-gray-400">
          {format(new Date(item.created_at), 'MMM d, yyyy HH:mm')}
        </span>
      ),
    },
    {
      key: 'domains_total',
      header: 'Domains',
      sortable: true,
      render: (item) => (
        <span className="font-medium text-gray-200">{item.domains_total}</span>
      ),
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
      key: 'user',
      header: 'User',
      render: (item) => (
        <span className="text-gray-400">{item.user || 'System'}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => <StatusBadge status={item.status} size="sm" />,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-100">Import History</h3>
        <p className="mt-1 text-sm text-gray-400">
          View all past domain import operations and their results.
        </p>
      </div>

      <DataTable
        columns={columns}
        data={data?.items || []}
        total={data?.total || 0}
        page={data?.page || 1}
        perPage={data?.per_page || 10}
        onPageChange={setPage}
        keyExtractor={(item) => item.id}
        emptyMessage="No import history found"
      />
    </div>
  );
}
