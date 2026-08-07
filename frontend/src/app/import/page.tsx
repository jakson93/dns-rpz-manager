'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  CheckCircle,
  FileText,
  Plus,
  Minus,
  Loader2,
} from 'lucide-react';
import api from '@/lib/api';
import FileUpload from '@/components/FileUpload';
import { Toast, ToastContainer, ToastType } from '@/components/Toast';

interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

interface ImportResult {
  id: number;
  filename: string;
  total_domains: number;
  new_domains: number;
  removed_domains: number;
  status: string;
}

export default function ImportPage() {
  const queryClient = useQueryClient();
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = (message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/v1/imports/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data as ImportResult;
    },
    onSuccess: (data) => {
      setImportResult(data);
      addToast(`Arquivo processado: ${data.new_domains} novos domínios encontrados`, 'success');
    },
    onError: () => {
      addToast('Falha ao importar arquivo. Verifique o formato.', 'error');
    },
  });

  const applyMutation = useMutation({
    mutationFn: async (importId: number) => {
      const response = await api.post(`/v1/imports/${importId}/apply`);
      return response.data;
    },
    onSuccess: () => {
      setImportResult(null);
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      queryClient.invalidateQueries({ queryKey: ['history'] });
      addToast('Importação aplicada com sucesso! RPZ atualizado e BIND recarregado.', 'success');
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.detail || 'Falha ao aplicar importação.';
      addToast(msg, 'error');
    },
  });

  const handleFileSelect = (file: File) => {
    setImportResult(null);
    uploadMutation.mutate(file);
  };

  const handleApply = () => {
    if (importResult) {
      applyMutation.mutate(importResult.id);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-100">
            Importar Lista de Bloqueio
          </h3>
          <p className="mt-1 text-sm text-gray-400">
            Envie um arquivo Excel (.xlsx) ou CSV contendo domínios para bloquear via DNS RPZ.
          </p>
        </div>

        <FileUpload
          onFileSelect={handleFileSelect}
          disabled={uploadMutation.isPending || applyMutation.isPending}
        />

        {uploadMutation.isPending && (
          <div className="mt-6 flex items-center justify-center gap-3 py-8">
            <Loader2 className="h-5 w-5 animate-spin text-brand-400" />
            <span className="text-sm text-gray-400">Processando arquivo...</span>
          </div>
        )}
      </div>

      {importResult && (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <div className="mb-4 flex items-center gap-3">
            <FileText className="h-5 w-5 text-brand-400" />
            <h3 className="text-lg font-semibold text-gray-100">
              Resultado da Importação
            </h3>
          </div>

          <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-gray-800 p-4">
              <div className="flex items-center gap-2 text-gray-400">
                <FileText className="h-4 w-4" />
                <span className="text-sm">Total de Domínios</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-100">
                {importResult.total_domains}
              </p>
            </div>
            <div className="rounded-lg bg-emerald-500/10 p-4">
              <div className="flex items-center gap-2 text-emerald-400">
                <Plus className="h-4 w-4" />
                <span className="text-sm">Novos Bloqueios</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-emerald-400">
                {importResult.new_domains}
              </p>
            </div>
            <div className="rounded-lg bg-gray-800 p-4">
              <div className="flex items-center gap-2 text-gray-400">
                <Minus className="h-4 w-4" />
                <span className="text-sm">Já existentes</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-400">
                {importResult.total_domains - importResult.new_domains}
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between border-t border-gray-800 pt-4">
            <button
              onClick={() => setImportResult(null)}
              className="rounded-lg border border-gray-700 px-4 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800"
            >
              Cancelar
            </button>
            <button
              onClick={handleApply}
              disabled={applyMutation.isPending}
              className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {applyMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Aplicando no DNS...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4" />
                  Confirmar e Aplicar
                </>
              )}
            </button>
          </div>
        </div>
      )}

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
