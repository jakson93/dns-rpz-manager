'use client';

import { useState } from 'react';
import Modal from './Modal';

interface AddDomainModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { domain: string; reason: string; added_by: string }) => void;
  isLoading?: boolean;
}

export default function AddDomainModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: AddDomainModalProps) {
  const [domain, setDomain] = useState('');
  const [reason, setReason] = useState('');
  const [addedBy, setAddedBy] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (domain.trim()) {
      onSubmit({
        domain: domain.trim(),
        reason: reason.trim(),
        added_by: addedBy.trim() || 'admin',
      });
      setDomain('');
      setReason('');
      setAddedBy('');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Domain">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Domain *
          </label>
          <input
            type="text"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="example.com"
            required
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Reason
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Why is this domain being blocked?"
            rows={3}
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 resize-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Added By
          </label>
          <input
            type="text"
            value={addedBy}
            onChange={(e) => setAddedBy(e.target.value)}
            placeholder="admin"
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
            disabled={isLoading || !domain.trim()}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Adding...' : 'Add Domain'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
