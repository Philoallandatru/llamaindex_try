// Shared types for the application

export interface ChatSession {
  session_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
}

export interface Source {
  source_id: string;
  source_type: string;
  title: string;
  url?: string;
  snippet: string;
  relevance_score: number;
}

export interface ChatResponse {
  message_id: string;
  content: string;
  sources: Source[];
  timestamp: string;
  metadata: Record<string, any>;
}
