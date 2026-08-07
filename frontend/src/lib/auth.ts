import { jwtDecode } from 'jwt-decode';

interface TokenPayload {
  sub: string;
  exp: number;
  iat: number;
  username?: string;
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('rpz_token');
}

export function setToken(token: string): void {
  localStorage.setItem('rpz_token', token);
}

export function removeToken(): void {
  localStorage.removeItem('rpz_token');
}

export function parseToken(token: string): TokenPayload | null {
  try {
    return jwtDecode<TokenPayload>(token);
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  const token = getToken();
  if (!token) return false;

  const payload = parseToken(token);
  if (!payload) return false;

  const currentTime = Date.now() / 1000;
  return payload.exp > currentTime;
}

export function getTokenUsername(): string | null {
  const token = getToken();
  if (!token) return null;

  const payload = parseToken(token);
  return payload?.username || payload?.sub || null;
}
