'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Search,
  Plus,
  RefreshCw,
  Globe,
  Filter,
  AlertCircle,
} from 'lucide-react';
import { format } from 'date-fns';
import api from '@/lib/api';
import DataTable, { Column } from '@/components/DataTable';
import StatusBadge from '@/components/StatusBadge';
import AddDomainModal from '@/components/AddDomainModal';
import { Toast, ToastContainer, ToastType } from '@/components/Toast';
import { Domain, DomainListResponse } from '@/types';

interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

export default function DomainsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [originFilter, setOriginFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = (message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const { data, isLoading, error } = useQuery<DomainListResponse>({
    queryKey: ['domains', page, search, originFilter, statusFilter],
    queryFn: async () => {
      const params: Record<string, unknown> = { page, per_page: 15 };
      if (search) params.search = search;
      if (originFilter) params.origin = originFilter;
      if (statusFilter) params.status = statusFilter;
      const response = await api.get('/v1/domains', { params });
      return response.data;
    },
  });

  const addDomainMutation = useMutation({
    mutationFn: async (data: { domain: string; reason: string; added_by: string }) => {
      const response = await api.post('/v1/domains', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setAddModalOpen(false);
      addToast('Domain added successfully', 'success');
    },
    onError: () => {
      addToast('Failed to add domain', 'error');
    },
  });

  const toggleStatusMutation = useMutation({
    mutationFn: async ({
      id,
      status,
    }: {
      id: number;
      status: string;
    }) => {
      const response = await api.patch(`/v1/domains/${id}`, {
        status: status === 'active' ? 'removed' : 'active',
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      addToast('Domain status updated', 'success');
    },
    onError: () => {
      addToast('Failed to update domain status', 'error');
    },
  });

  const columns: Column<Domain>[] = [
    {
      key: 'domain',
      header: 'Domain',
      sortable: true,
      render: (item) => (
        <div className="flex items-center gap-2">
          <Globe className="h-4 w-4 text-gray-500" />
          <span className="font-mono font-medium text-gray-200">
            {item.domain}
          </span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => <StatusBadge status={item.status} size="sm" />,
    },
    {
      key: 'origin',
      header: 'Origin',
      render: (item) => (
        <span className="capitalize text-gray-400">{item.origin}</span>
      ),
    },
    {
      key: 'rpz_action',
      header: 'Action',
      render: (item) => (
        <span className="font-mono text-xs text-gray-400">
          {item.rpz_action}
        </span>
      ),
    },
    {
      key: 'reason',
      header: 'Reason',
      render: (item) => (
        <span className="text-gray-400 truncate max-w-[200px] block">
          {item.reason || '-'}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Added',
      sortable: true,
      render: (item) => (
        <span className="text-gray-400">
          {format(new Date(item.created_at), 'MMM d, yyyy')}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (item) => (
        <button
          onClick={() =>
            toggleStatusMutation.mutate({
              id: item.id,
              status: item.status,
            })
          }
          disabled={toggleStatusMutation.isPending}
          className="rounded-lg border border-gray-700 px-3 py-1 text-xs font-medium text-gray-300 hover:bg-gray-800 disabled:opacity-50"
        >
          {item.status === 'active' ? 'Remove' : 'Restore'}
        </button>
      ),
      className: 'text-right',
    },
  ];

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-200">
          Failed to load domains
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Please check your connection and try again.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-100">
            Domains Management
          </h3>
          <p className="mt-1 text-sm text-gray-400">
            Manage blocked domains in the RPZ zone.
          </p>
        </div>
        <button
          onClick={() => setAddModalOpen(true)}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          Add Domain
        </button>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search domains..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-gray-700 bg-gray-800 pl-10 pr-4 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div className="flex gap-3">
          <select
            value={originFilter}
            onChange={(e) => {
              setOriginFilter(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-300 focus:border-brand-500 focus:outline-none"
          >
            <option value="">All Origins</option>
            <option value="excel">Excel</option>
            <option value="manual">Manual</option>
            <option value="api">API</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-300 focus:border-brand-500 focus:outline-none"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="removed">Removed</option>
          </select>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={data?.domains || []}
        total={data?.total || 0}
        page={data?.page || 1}
        perPage={data?.per_page || 15}
        onPageChange={setPage}
        keyExtractor={(item) => item.id}
        emptyMessage="No domains found"
      />

      <AddDomainModal
        isOpen={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onSubmit={(data) => addDomainMutation.mutate(data)}
        isLoading={addDomainMutation.isPending}
      />

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
