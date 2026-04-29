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
    knowledgeBaseId?: string | null,
    modelId?: string | null,
    retrievalMode = 'hybrid',
    similarityTopK = 5
  ) => {
    const { data } = await api.post<ChatResponse>('/api/chat/message', {
      session_id: sessionId,
      message,
      retrieval_mode: retrievalMode,
      similarity_top_k: similarityTopK,
      knowledge_base_id: knowledgeBaseId,
      model_id: modelId,
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

export const reportsApi = {
  generateReport: async (date: string, mode: 'quick' | 'full' = 'quick') => {
    const { data } = await api.post('/api/reports/daily', {
      date,
      mode,
    });
    return data;
  },

  getReport: async (reportId: string) => {
    const { data } = await api.get(`/api/reports/daily/${reportId}`);
    return data;
  },

  getSavedReport: async (date: string) => {
    const { data } = await api.get(`/api/reports/daily/saved/${date}`);
    return data;
  },

  listReports: async () => {
    const { data } = await api.get('/api/reports/daily/list');
    return data.reports || [];
  },
};

// Data Source API
export const datasourceApi = {
  list: async () => {
    const { data } = await api.get('/api/datasources');
    return data;
  },

  get: async (id: string) => {
    const { data } = await api.get(`/api/datasources/${id}`);
    return data;
  },

  create: async (datasource: any) => {
    const { data } = await api.post('/api/datasources', datasource);
    return data;
  },

  update: async (id: string, datasource: any) => {
    const { data } = await api.put(`/api/datasources/${id}`, datasource);
    return data;
  },

  delete: async (id: string) => {
    const { data } = await api.delete(`/api/datasources/${id}`);
    return data;
  },

  sync: async (id: string) => {
    const { data } = await api.post(`/api/datasources/${id}/sync`);
    return data;
  },

  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('files', file);  // Changed from 'file' to 'files' to match backend
    const { data } = await api.post('/api/datasources/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};

// Knowledge Base API
export const knowledgeBaseApi = {
  list: async () => {
    const { data } = await api.get('/api/knowledge-bases');
    return data;
  },

  get: async (id: string) => {
    const { data } = await api.get(`/api/knowledge-bases/${id}`);
    return data;
  },

  create: async (kb: any) => {
    const { data } = await api.post('/api/knowledge-bases', kb);
    return data;
  },

  update: async (id: string, kb: any) => {
    const { data } = await api.put(`/api/knowledge-bases/${id}`, kb);
    return data;
  },

  delete: async (id: string) => {
    const { data } = await api.delete(`/api/knowledge-bases/${id}`);
    return data;
  },

  sync: async (id: string) => {
    const { data } = await api.post(`/api/knowledge-bases/${id}/sync`);
    return data;
  },
};

// Model Configuration API
export const modelApi = {
  list: async () => {
    const { data } = await api.get('/api/models');
    return data;
  },

  get: async (id: string) => {
    const { data } = await api.get(`/api/models/${id}`);
    return data;
  },

  create: async (model: any) => {
    const { data } = await api.post('/api/models', model);
    return data;
  },

  update: async (id: string, model: any) => {
    const { data } = await api.put(`/api/models/${id}`, model);
    return data;
  },

  delete: async (id: string) => {
    const { data } = await api.delete(`/api/models/${id}`);
    return data;
  },

  setDefault: async (id: string) => {
    const { data } = await api.post(`/api/models/${id}/set-default`);
    return data;
  },

  getDefault: async () => {
    const { data } = await api.get('/api/models/default');
    return data;
  },
};

export default api;
