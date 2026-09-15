import type { AvailabilityResult } from './availability';

export type ChatRole = 'user' | 'assistant';

export type ChatProgressStep = 'connecting' | 'checking' | 'preparing';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  responseType?: ChatResponseType;
  sources?: Array<{ title: string; url: string }>;
}

export interface ConversationEntry {
  role: ChatRole;
  content: string;
}

export type ChatResponseType = 'answer' | 'availability' | 'clarification' | 'fallback';

export interface ChatResponse {
  success: boolean;
  type: ChatResponseType;
  message: string;
  conversation_id: string;
  availability?: AvailabilityResult | null;
  sources?: Array<{ title: string; url: string }>;
}
