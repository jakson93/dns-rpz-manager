export interface User {
  id: number;
  username: string;
  email?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface Domain {
  id: number;
  domain: string;
  rpz_action: 'nxdomain' | 'passthru' | 'cname' | 'none';
  status: 'active' | 'removed';
  origin: 'excel' | 'manual' | 'api';
  reason?: string;
  added_by?: string;
  created_at: string;
  updated_at: string;
}

export interface DomainCreate {
  domain: string;
  rpz_action?: string;
  reason?: string;
  added_by?: string;
}

export interface DomainListResponse {
  domains: Domain[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface DNSServer {
  id: number;
  name: string;
  ip_address: string;
  port: number;
  status: 'active' | 'inactive' | 'error';
  last_sync?: string;
  created_at: string;
}

export interface DNSServerCreate {
  name: string;
  ip_address: string;
  port?: number;
}

export interface ImportJob {
  id: number;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  domains_added: number;
  domains_removed: number;
  domains_total: number;
  error_message?: string;
  user?: string;
  created_at: string;
  completed_at?: string;
}

export interface ImportPreview {
  filename: string;
  total_domains: number;
  new_domains: number;
  existing_domains: number;
  domains: string[];
}

export interface AuditLog {
  id: number;
  event: string;
  description: string;
  user: string;
  ip_address?: string;
  created_at: string;
}

export interface AuditLogListResponse {
  logs: AuditLog[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface DashboardStats {
  total_blocked_domains: number;
  active_domains: number;
  removed_domains: number;
  total_imports: number;
  last_import_date?: string;
  dns_servers_online: number;
  dns_servers_total: number;
  domains_added_this_week: number;
  domains_removed_this_week: number;
}

export interface RecentImport {
  id: number;
  filename: string;
  status: string;
  domains_added: number;
  domains_removed: number;
  created_at: string;
}

export interface DashboardData {
  stats: DashboardStats;
  recent_imports: RecentImport[];
  daily_stats: DailyStat[];
}

export interface DailyStat {
  date: string;
  added: number;
  removed: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}
