import { useState, useEffect, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { chatApi, ChatMessage, ChatSession } from '../utils/api';
import '../styles/globals.css';

export default function ChatPage() {
  const navigate = useNavigate();
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Fetch sessions
  const { data: sessionsData } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => chatApi.listSessions(),
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
      chatApi.sendMessage(currentSessionId!, message),
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

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 style={{ color: 'var(--sidebar-text)', fontSize: '18px', marginBottom: '16px' }}>
            SSD Knowledge Portal
          </h2>
          <button
            className="new-chat-btn"
            onClick={() => createSessionMutation.mutate()}
          >
            + New Chat
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
            onClick={() => navigate('/issues')}
          >
            🔍 Issues Analysis
          </div>
          <div
            className="conversation-item"
            onClick={() => navigate('/reports')}
          >
            📊 Daily Reports
          </div>
          <div
            className="conversation-item"
            onClick={() => navigate('/knowledge')}
          >
            📚 Knowledge Base
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
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? 'U' : 'AI'}
              </div>
              <div className="message-content">
                <div>{msg.content}</div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    <strong>Sources:</strong>
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
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              className="message-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Send a message..."
              rows={1}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim() || sendMessageMutation.isPending}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
