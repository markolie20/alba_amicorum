import { Album } from './types';

const API_BASE = 'http://localhost:8000';

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

export const fetchAlbums = (): Promise<Album[]> =>
  apiFetch('/api/albums');

export const fetchAlbumDetail = (id: string): Promise<Album> =>
  apiFetch(`/api/albums/${id}`);

export const fetchCountries = (): Promise<string[]> =>
  apiFetch('/api/countries');
