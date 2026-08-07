'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Server,
  Plus,
  RefreshCw,
  Edit2,
  Trash2,
  Wifi,
  WifiOff,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { format } from 'date-fns';
import api from '@/lib/api';
import AddServerModal from '@/components/AddServerModal';
import StatusBadge from '@/components/StatusBadge';
import { Toast, ToastContainer, ToastType } from '@/components/Toast';
import { DNSServer } from '@/types';

interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

export default function ServersPage() {
  const queryClient = useQueryClient();
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [editingServer, setEditingServer] = useState<DNSServer | null>(null);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = (message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const { data: servers, isLoading, error } = useQuery<DNSServer[]>({
    queryKey: ['servers'],
    queryFn: async () => {
      const response = await api.get('/v1/servers');
      return response.data?.items || response.data || [];
    },
  });

  const addServerMutation = useMutation({
    mutationFn: async (data: {
      name: string;
      ip_address: string;
      port: number;
    }) => {
      const response = await api.post('/v1/servers', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      setAddModalOpen(false);
      addToast('Server added successfully', 'success');
    },
    onError: () => {
      addToast('Failed to add server', 'error');
    },
  });

  const updateServerMutation = useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: number;
      data: { name: string; ip_address: string; port: number };
    }) => {
      const response = await api.put(`/v1/servers/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      setEditingServer(null);
      addToast('Server updated successfully', 'success');
    },
    onError: () => {
      addToast('Failed to update server', 'error');
    },
  });

  const deleteServerMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/v1/servers/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      addToast('Server deleted successfully', 'success');
    },
    onError: () => {
      addToast('Failed to delete server', 'error');
    },
  });

  const reloadServerMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post(`/v1/servers/${id}/reload`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] });
      addToast('Server reloaded successfully', 'success');
    },
    onError: () => {
      addToast('Failed to reload server', 'error');
    },
  });

  const handleEdit = (server: DNSServer) => {
    setEditingServer(server);
    setAddModalOpen(true);
  };

  const handleDelete = (server: DNSServer) => {
    if (
      window.confirm(
        `Are you sure you want to delete server "${server.name}"?`
      )
    ) {
      deleteServerMutation.mutate(server.id);
    }
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-200">
          Failed to load servers
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
          <h3 className="text-lg font-semibold text-gray-100">DNS Servers</h3>
          <p className="mt-1 text-sm text-gray-400">
            Manage DNS servers configured for RPZ zone transfers.
          </p>
        </div>
        <button
          onClick={() => {
            setEditingServer(null);
            setAddModalOpen(true);
          }}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          Add Server
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
        </div>
      ) : !servers || servers.length === 0 ? (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-12 text-center">
          <Server className="mx-auto h-12 w-12 text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-300">No servers configured</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add a DNS server to start managing RPZ zones.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {servers.map((server) => (
            <div
              key={server.id}
              className="rounded-xl border border-gray-800 bg-gray-900 p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                      server.status === 'active'
                        ? 'bg-emerald-500/10'
                        : server.status === 'error'
                          ? 'bg-red-500/10'
                          : 'bg-gray-800'
                    }`}
                  >
                    {server.status === 'active' ? (
                      <Wifi className="h-5 w-5 text-emerald-400" />
                    ) : (
                      <WifiOff
                        className={`h-5 w-5 ${
                          server.status === 'error'
                            ? 'text-red-400'
                            : 'text-gray-500'
                        }`}
                      />
                    )}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-100">{server.name}</h4>
                    <p className="text-sm font-mono text-gray-400">
                      {server.ip_address}:{server.port}
                    </p>
                  </div>
                </div>
                <StatusBadge status={server.status} size="sm" />
              </div>

              {server.last_sync && (
                <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
                  <Clock className="h-3 w-3" />
                  Last sync:{' '}
                  {format(new Date(server.last_sync), 'MMM d, yyyy HH:mm')}
                </div>
              )}

              <div className="mt-4 flex items-center gap-2 border-t border-gray-800 pt-4">
                <button
                  onClick={() => reloadServerMutation.mutate(server.id)}
                  disabled={reloadServerMutation.isPending}
                  className="flex items-center gap-1.5 rounded-lg border border-gray-700 px-3 py-1.5 text-xs font-medium text-gray-300 hover:bg-gray-800 disabled:opacity-50"
                >
                  <RefreshCw
                    className={`h-3.5 w-3.5 ${
                      reloadServerMutation.isPending ? 'animate-spin' : ''
                    }`}
                  />
                  Reload
                </button>
                <button
                  onClick={() => handleEdit(server)}
                  className="flex items-center gap-1.5 rounded-lg border border-gray-700 px-3 py-1.5 text-xs font-medium text-gray-300 hover:bg-gray-800"
                >
                  <Edit2 className="h-3.5 w-3.5" />
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(server)}
                  disabled={deleteServerMutation.isPending}
                  className="flex items-center gap-1.5 rounded-lg border border-red-800/50 px-3 py-1.5 text-xs font-medium text-red-400 hover:bg-red-500/10 disabled:opacity-50"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <AddServerModal
        isOpen={addModalOpen}
        onClose={() => {
          setAddModalOpen(false);
          setEditingServer(null);
        }}
        onSubmit={(data) => {
          if (editingServer) {
            updateServerMutation.mutate({ id: editingServer.id, data });
          } else {
            addServerMutation.mutate(data);
          }
        }}
        server={editingServer}
        isLoading={addServerMutation.isPending || updateServerMutation.isPending}
      />

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
