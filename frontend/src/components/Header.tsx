'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { LogOut, User, ChevronDown } from 'lucide-react';
import { removeToken, getTokenUsername } from '@/lib/auth';
import { cn } from '@/lib/utils';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/import': 'Import Domains',
  '/domains': 'Domains Management',
  '/servers': 'DNS Servers',
  '/history': 'Import History',
  '/logs': 'Audit Logs',
};

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    setUsername(getTokenUsername());
  }, []);

  const title = pageTitles[pathname || ''] || 'DNS RPZ Manager';

  const handleLogout = () => {
    removeToken();
    router.push('/login');
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-800 bg-gray-900/50 px-6 backdrop-blur-sm">
      <h2 className="text-xl font-semibold text-gray-100">{title}</h2>

      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-300 hover:bg-gray-800"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-700">
            <User className="h-4 w-4 text-gray-300" />
          </div>
          <span className="hidden sm:inline">{username || 'Admin'}</span>
          <ChevronDown className="h-4 w-4" />
        </button>

        {dropdownOpen && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setDropdownOpen(false)}
            />
            <div className="absolute right-0 z-50 mt-2 w-48 rounded-lg border border-gray-700 bg-gray-800 py-1 shadow-xl">
              <div className="border-b border-gray-700 px-4 py-2">
                <p className="text-sm font-medium text-gray-200">
                  {username || 'Admin'}
                </p>
                <p className="text-xs text-gray-500">Administrator</p>
              </div>
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-gray-700/50"
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
