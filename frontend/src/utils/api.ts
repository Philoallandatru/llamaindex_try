import axios from 'axios';
import type { ChatSession, ChatMessage, Source, ChatResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Re-export types for convenience
export { ChatSession, ChatMessage, Source, ChatResponse };

// API functions
export const chatApi = {
  // Sessions
  createSession: async (name?: string) => {
    const { data } = await api.post('/api/chat/sessions', { name });
    return data;
  },

  listSessions: async (limit = 20, offset = 0) => {
    const { data } = await api.get('/api/chat/sessions', {
      params: { limit, offset },
    });
    return data;
  },

  getSession: async (sessionId: string) => {
    const { data } = await api.get(`/api/chat/sessions/${sessionId}`);
    return data;
  },

  deleteSession: async (sessionId: string) => {
    const { data } = await api.delete(`/api/chat/sessions/${sessionId}`);
    return data;
  },

  // Messages
  sendMessage: async (
    sessionId: string,
    message: string,
    retrievalMode = 'hybrid',
    similarityTopK = 5
  ) => {
    const { data } = await api.post<ChatResponse>('/api/chat/message', {
      session_id: sessionId,
      message,
      retrieval_mode: retrievalMode,
      similarity_top_k: similarityTopK,
    });
    return data;
  },

  getHistory: async (sessionId: string, maxMessages?: number) => {
    const { data } = await api.get(`/api/chat/sessions/${sessionId}/history`, {
      params: { max_messages: maxMessages },
    });
    return data;
  },
};

export const indexApi = {
  getStats: async () => {
    const { data } = await api.get('/api/index/stats');
    return data;
  },

  getStatus: async () => {
    const { data } = await api.get('/api/index/status');
    return data;
  },
};

export const analysisApi = {
  analyzeIssue: async (
    issueKey: string,
    depth: 'quick' | 'deep' = 'deep',
    includeRelated: boolean = true,
    saveToKb: boolean = true
  ) => {
    const { data } = await api.post(`/api/analysis/issue/${issueKey}`, {
      issue_key: issueKey,
      depth,
      include_related: includeRelated,
      save_to_kb: saveToKb,
    });
    return data;
  },

  getSavedAnalysis: async (issueKey: string) => {
    const { data } = await api.get(`/api/analysis/issue/${issueKey}`);
    return data;
  },

  listAnalyzedIssues: async () => {
    const { data } = await api.get('/api/analysis/issues');
    return data;
  },
};

export const sourceApi = {
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/api/sources/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  testJira: async (config: any) => {
    const { data } = await api.post('/api/sources/jira/test', config);
    return data;
  },

  syncJira: async (config: any) => {
    const { data } = await api.post('/api/sources/jira/sync', config);
    return data;
  },
};

export default api;
