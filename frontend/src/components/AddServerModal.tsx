'use client';

import { useState, useEffect } from 'react';
import Modal from './Modal';
import { DNSServer } from '@/types';

interface AddServerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; ip_address: string; port: number }) => void;
  server?: DNSServer | null;
  isLoading?: boolean;
}

export default function AddServerModal({
  isOpen,
  onClose,
  onSubmit,
  server,
  isLoading = false,
}: AddServerModalProps) {
  const [name, setName] = useState('');
  const [ipAddress, setIpAddress] = useState('');
  const [port, setPort] = useState('53');

  useEffect(() => {
    if (server) {
      setName(server.name);
      setIpAddress(server.ip_address);
      setPort(String(server.port));
    } else {
      setName('');
      setIpAddress('');
      setPort('53');
    }
  }, [server, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() && ipAddress.trim()) {
      onSubmit({
        name: name.trim(),
        ip_address: ipAddress.trim(),
        port: parseInt(port) || 53,
      });
      setName('');
      setIpAddress('');
      setPort('53');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={server ? 'Edit DNS Server' : 'Add DNS Server'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Server Name *
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Primary DNS"
            required
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            IP Address *
          </label>
          <input
            type="text"
            value={ipAddress}
            onChange={(e) => setIpAddress(e.target.value)}
            placeholder="192.168.1.1"
            required
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Port
          </label>
          <input
            type="number"
            value={port}
            onChange={(e) => setPort(e.target.value)}
            min="1"
            max="65535"
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-gray-700 px-4 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading || !name.trim() || !ipAddress.trim()}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading
              ? server
                ? 'Saving...'
                : 'Adding...'
              : server
                ? 'Save Changes'
                : 'Add Server'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
