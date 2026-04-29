import { useState, useEffect, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { chatApi, knowledgeBaseApi, modelApi } from '../utils/api';
import type { ChatMessage, ChatSession } from '../types';
import '../styles/globals.css';

const SUGGESTIONS = [
  {
    title: "Explain a concept",
    text: "What is LlamaIndex and how does it work?"
  },
  {
    title: "Search knowledge base",
    text: "Find information about data sources configuration"
  },
  {
    title: "Technical question",
    text: "How do I integrate Jira with this system?"
  },
  {
    title: "Get started",
    text: "What can you help me with?"
  }
];

export default function ChatPage() {
  const navigate = useNavigate();
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [selectedKbId, setSelectedKbId] = useState<string | null>(null);
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const queryClient = useQueryClient();

  // Fetch sessions
  const { data: sessionsData } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => chatApi.listSessions(),
  });

  // Fetch knowledge bases
  const { data: knowledgeBases } = useQuery({
    queryKey: ['knowledgeBases'],
    queryFn: () => knowledgeBaseApi.list(),
  });

  // Fetch models
  const { data: models } = useQuery({
    queryKey: ['models'],
    queryFn: () => modelApi.list(),
  });

  // Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: () => chatApi.createSession(),
    onSuccess: (data) => {
      setCurrentSessionId(data.session_id);
      setMessages([]);
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (message: string) =>
      chatApi.sendMessage(currentSessionId!, message, selectedKbId, selectedModelId),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.content,
          timestamp: data.timestamp,
          sources: data.sources,
        },
      ]);
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  // Create initial session
  useEffect(() => {
    if (!currentSessionId && !createSessionMutation.isPending) {
      createSessionMutation.mutate();
    }
  }, []);

  const handleSend = () => {
    if (!input.trim() || !currentSessionId) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    sendMessageMutation.mutate(input);
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (text: string) => {
    setInput(text);
    textareaRef.current?.focus();
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 style={{ fontSize: '16px', marginBottom: '12px', fontWeight: 600 }}>
            Knowledge Portal
          </h2>
          <button
            className="new-chat-btn"
            onClick={() => createSessionMutation.mutate()}
          >
            <span>+</span> New Chat
          </button>
        </div>
        <div style={{ padding: '12px', borderBottom: '1px solid var(--border-color)' }}>
          <div
            className="conversation-item active"
            style={{ marginBottom: '4px' }}
          >
            💬 Chat
          </div>
          <div
            className="conversation-item"
            onClick={() => navigate('/knowledge')}
          >
            📚 Knowledge Base
          </div>
          <div
            className="conversation-item"
            onClick={() => navigate('/datasources')}
          >
            🗄️ Data Sources
          </div>
          <div
            className="conversation-item"
            onClick={() => navigate('/models')}
          >
            🤖 Models
          </div>
        </div>
        <div className="conversation-list">
          {sessionsData?.sessions?.map((session: ChatSession) => (
            <div
              key={session.session_id}
              className={`conversation-item ${
                session.session_id === currentSessionId ? 'active' : ''
              }`}
              onClick={() => {
                setCurrentSessionId(session.session_id);
                chatApi.getHistory(session.session_id).then((data) => {
                  setMessages(data.messages);
                });
              }}
            >
              {session.name}
            </div>
          ))}
        </div>
      </div>

      {/* Main Panel */}
      <div className="main-panel">
        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">💡</div>
              <h1 className="empty-state-title">How can I help you today?</h1>
              <p className="empty-state-subtitle">
                Ask me anything about your knowledge base, documents, or get insights from your data sources.
              </p>
              <div className="suggestion-cards">
                {SUGGESTIONS.map((suggestion, idx) => (
                  <div
                    key={idx}
                    className="suggestion-card"
                    onClick={() => handleSuggestionClick(suggestion.text)}
                  >
                    <div className="suggestion-card-title">{suggestion.title}</div>
                    <div className="suggestion-card-text">{suggestion.text}</div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? 'U' : 'AI'}
                  </div>
                  <div className="message-content">
                    <div>{msg.content}</div>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources">
                        <strong>Sources</strong>
                        {msg.sources.map((source, i) => (
                          <div key={i} className="source-card">
                            <div className="source-title">{source.title}</div>
                            <div className="source-snippet">{source.snippet}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {sendMessageMutation.isPending && (
                <div className="message assistant">
                  <div className="message-avatar">AI</div>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="input-container">
          <div className="config-bar">
            <div className="config-item">
              <label className="config-label">Knowledge Base</label>
              <select
                value={selectedKbId || ''}
                onChange={(e) => setSelectedKbId(e.target.value || null)}
                className="config-select"
              >
                <option value="">Default</option>
                {knowledgeBases?.map((kb: any) => (
                  <option key={kb.id} value={kb.id}>
                    {kb.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="config-item">
              <label className="config-label">Model</label>
              <select
                value={selectedModelId || ''}
                onChange={(e) => setSelectedModelId(e.target.value || null)}
                className="config-select"
              >
                <option value="">Default</option>
                {models?.map((model: any) => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              className="message-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message Knowledge Portal..."
              rows={1}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim() || sendMessageMutation.isPending}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
