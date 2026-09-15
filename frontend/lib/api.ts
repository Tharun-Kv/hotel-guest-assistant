import { API_TIMEOUT_MS } from './constants';
import type { ApiErrorPayload, HotelInformation } from '@/types/api';
import type { AvailabilityResult } from '@/types/availability';
import type { ChatResponse, ConversationEntry } from '@/types/chat';

export interface KnowledgeDocument {
  document_id: string;
  hotel_id: string;
  title: string;
  source_url: string;
  ingested_at: string;
  chunk_count: number;
}

export interface KnowledgeSearchResult {
  chunk_id: string;
  title: string;
  source_url: string;
  text: string;
  score: number;
}

export interface InventorySnapshot {
  hotel_id: string;
  last_synced_at: string | null;
  rooms: Array<Record<string, unknown>>;
  bookings: Array<Record<string, unknown>>;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(message: string, public readonly status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    });
    const payload: unknown = await response.json().catch(() => null);

    if (!response.ok) {
      const error = payload as ApiErrorPayload | null;
      throw new ApiError(error?.error || error?.detail || 'The request could not be completed.', response.status);
    }
    if (!payload || typeof payload !== 'object') {
      throw new ApiError('The server returned an unexpected response.');
    }
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('The request timed out. Please try again.');
    }
    throw new ApiError('Unable to reach the hotel assistant. Please check your connection and try again.');
  } finally {
    window.clearTimeout(timeout);
  }
}

function adminHeaders(token: string): HeadersInit {
  return token.trim() ? { 'X-Admin-Token': token.trim() } : {};
}

export function sendChatMessage(
  message: string,
  conversationId: string | null,
  conversation: ConversationEntry[] = [],
): Promise<ChatResponse> {
  return request<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message, conversation_id: conversationId, conversation }),
  });
}

export function checkAvailability(checkIn: string, checkOut: string, adults: number, hotelId = 'default'): Promise<AvailabilityResult> {
  return request<AvailabilityResult>('/api/availability', {
    method: 'POST',
    body: JSON.stringify({ hotel_id: hotelId, check_in: checkIn, check_out: checkOut, adults }),
  });
}

export function getHotelInformation(): Promise<HotelInformation> {
  return request<HotelInformation>('/api/hotel');
}

export function searchKnowledge(query: string, hotelId = 'default'): Promise<{ results: KnowledgeSearchResult[] }> {
  return request('/api/knowledge/search', {
    method: 'POST',
    body: JSON.stringify({ query, hotel_id: hotelId, top_k: 5 }),
  });
}

export function listKnowledgeDocuments(token: string, hotelId = 'default'): Promise<KnowledgeDocument[]> {
  return request(`/api/admin/knowledge/documents?hotel_id=${encodeURIComponent(hotelId)}`, {
    headers: adminHeaders(token),
  });
}

export function ingestKnowledgeSource(payload: { url?: string; content?: string; title?: string; hotel_id?: string; source_url?: string }, token: string): Promise<{ document: KnowledgeDocument }> {
  return request('/api/admin/knowledge/ingest', {
    method: 'POST',
    headers: adminHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function getLiveInventory(token: string, hotelId = 'default'): Promise<InventorySnapshot> {
  return request(`/api/admin/inventory?hotel_id=${encodeURIComponent(hotelId)}`, { headers: adminHeaders(token) });
}

export function updateLiveInventory(snapshot: InventorySnapshot, token: string): Promise<InventorySnapshot> {
  return request('/api/admin/inventory', {
    method: 'PUT',
    headers: adminHeaders(token),
    body: JSON.stringify(snapshot),
  });
}
