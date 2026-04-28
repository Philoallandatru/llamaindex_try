import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, Plus, Trash2, Star, Settings } from 'lucide-react';
import { modelApi } from '../utils/api';
import '../styles/globals.css';

interface Model {
  id: string;
  name: string;
  api_base: string;
  model_name: string;
  is_default: boolean;
  status: string;
  parameters: {
    temperature: number;
    max_tokens: number;
    top_p: number;
  };
  created_at: string;
}

export default function ModelsPage() {
  const navigate = useNavigate();
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    api_base: 'http://localhost:1234/v1',
    api_key: 'not-needed',
    model_name: '',
    temperature: 0.7,
    max_tokens: 2000,
    top_p: 0.9,
    is_default: false,
  });

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const data = await modelApi.list();
      setModels(data);
    } catch (error) {
      console.error('Failed to load models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await modelApi.create({
        name: formData.name,
        api_base: formData.api_base,
        api_key: formData.api_key,
        model_name: formData.model_name,
        parameters: {
          temperature: formData.temperature,
          max_tokens: formData.max_tokens,
          top_p: formData.top_p,
        },
        is_default: formData.is_default,
      });
      setShowCreateModal(false);
      setFormData({
        name: '',
        api_base: 'http://localhost:1234/v1',
        api_key: 'not-needed',
        model_name: '',
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 0.9,
        is_default: false,
      });
      loadModels();
    } catch (error) {
      console.error('Failed to create model:', error);
      alert('Failed to create model');
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await modelApi.setDefault(id);
      loadModels();
    } catch (error) {
      console.error('Failed to set default model:', error);
      alert('Failed to set default model');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this model?')) return;

    try {
      await modelApi.delete(id);
      loadModels();
    } catch (error) {
      console.error('Failed to delete model:', error);
      alert('Failed to delete model');
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 style={{ fontSize: '16px', marginBottom: '12px', fontWeight: 600 }}>
            Knowledge Portal
          </h2>
          <button className="new-chat-btn" onClick={() => navigate('/')}>
            <span>💬</span> Chat
          </button>
        </div>
        <div style={{ padding: '12px', borderBottom: '1px solid var(--border-color)' }}>
          <div className="conversation-item" onClick={() => navigate('/')}>
            Chat
          </div>
          <div className="conversation-item" onClick={() => navigate('/datasources')}>
            Data Sources
          </div>
          <div className="conversation-item" onClick={() => navigate('/knowledge')}>
            Knowledge Base
          </div>
          <div className="conversation-item active" onClick={() => navigate('/models')}>
            Models
          </div>
        </div>
      </div>

      {/* Main Panel */}
      <div className="main-panel">
        <div className="chat-container" style={{ padding: '40px 24px' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '32px'
            }}>
              <div>
                <h1 style={{ fontSize: '28px', fontWeight: 600, marginBottom: '8px' }}>
                  Model Configurations
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                  Configure local and remote LLM models
                </p>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="new-chat-btn"
                style={{ width: 'auto', padding: '12px 24px' }}
              >
                <Plus size={18} />
                <span>Add Model</span>
              </button>
            </div>

            {/* Loading State */}
            {loading && (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <div className="typing-indicator" style={{ justifyContent: 'center' }}>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!loading && models.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon"><Cpu size={64} /></div>
                <h2 className="empty-state-title">No models configured</h2>
                <p className="empty-state-subtitle">
                  Add your first model configuration to start using local LLMs
                </p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="new-chat-btn"
                  style={{ marginTop: '24px', width: 'auto', padding: '12px 24px' }}
                >
                  <Plus size={18} />
                  <span>Add Model</span>
                </button>
              </div>
            )}

            {/* Models Grid */}
            {!loading && models.length > 0 && (
              <div style={{ display: 'grid', gap: '16px' }}>
                {models.map((model) => (
                  <div
                    key={model.id}
                    className="source-card"
                    style={{ cursor: 'default' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                          <div style={{ color: 'var(--accent)' }}>
                            <Cpu size={20} />
                          </div>
                          <h3 className="source-title" style={{ margin: 0 }}>{model.name}</h3>
                          {model.is_default && (
                            <span style={{
                              padding: '4px 10px',
                              backgroundColor: '#10b981',
                              color: 'white',
                              borderRadius: '6px',
                              fontSize: '11px',
                              fontWeight: 600,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}>
                              <Star size={12} fill="white" />
                              Default
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                          <div style={{ marginBottom: '4px' }}>
                            <strong>Model:</strong> {model.model_name}
                          </div>
                          <div style={{ marginBottom: '4px' }}>
                            <strong>API Base:</strong> {model.api_base}
                          </div>
                          <div style={{ display: 'flex', gap: '16px', marginTop: '8px', fontSize: '13px' }}>
                            <span>Temperature: {model.parameters.temperature}</span>
                            <span>Max Tokens: {model.parameters.max_tokens}</span>
                            <span>Top P: {model.parameters.top_p}</span>
                          </div>
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          Created {new Date(model.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        {!model.is_default && (
                          <button
                            onClick={() => handleSetDefault(model.id)}
                            style={{
                              padding: '8px 16px',
                              backgroundColor: 'var(--accent)',
                              color: 'white',
                              border: 'none',
                              borderRadius: '8px',
                              cursor: 'pointer',
                              fontSize: '13px',
                              fontWeight: 600,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              transition: 'all 0.2s'
                            }}
                          >
                            <Star size={14} />
                            Set Default
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(model.id)}
                          style={{
                            padding: '8px 12px',
                            backgroundColor: 'transparent',
                            color: 'var(--text-secondary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontSize: '13px',
                            display: 'flex',
                            alignItems: 'center',
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = '#ef4444';
                            e.currentTarget.style.color = '#ef4444';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = 'var(--border-color)';
                            e.currentTarget.style.color = 'var(--text-secondary)';
                          }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 50,
          backdropFilter: 'blur(4px)'
        }}>
          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: '16px',
            padding: '32px',
            width: '100%',
            maxWidth: '500px',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: 'var(--shadow-xl)',
            border: '1px solid var(--border-color)'
          }}>
            <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '24px' }}>
              Add Model Configuration
            </h2>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="message-input"
                style={{
                  padding: '12px 16px',
                  border: '1.5px solid var(--border-color)',
                  borderRadius: '10px',
                  backgroundColor: 'var(--input-bg)'
                }}
                placeholder="Qwen 2.5 Coder 7B"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                API Base URL
              </label>
              <input
                type="text"
                value={formData.api_base}
                onChange={(e) => setFormData({ ...formData, api_base: e.target.value })}
                className="message-input"
                style={{
                  padding: '12px 16px',
                  border: '1.5px solid var(--border-color)',
                  borderRadius: '10px',
                  backgroundColor: 'var(--input-bg)'
                }}
                placeholder="http://localhost:1234/v1"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                API Key
              </label>
              <input
                type="password"
                value={formData.api_key}
                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                className="message-input"
                style={{
                  padding: '12px 16px',
                  border: '1.5px solid var(--border-color)',
                  borderRadius: '10px',
                  backgroundColor: 'var(--input-bg)'
                }}
                placeholder="Optional for local models"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Model Name
              </label>
              <input
                type="text"
                value={formData.model_name}
                onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                className="message-input"
                style={{
                  padding: '12px 16px',
                  border: '1.5px solid var(--border-color)',
                  borderRadius: '10px',
                  backgroundColor: 'var(--input-bg)'
                }}
                placeholder="qwen2.5-coder-7b-instruct"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Temperature: {formData.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={formData.temperature}
                onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Max Tokens
              </label>
              <input
                type="number"
                value={formData.max_tokens}
                onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                className="message-input"
                style={{
                  padding: '12px 16px',
                  border: '1.5px solid var(--border-color)',
                  borderRadius: '10px',
                  backgroundColor: 'var(--input-bg)'
                }}
                placeholder="2000"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={formData.is_default}
                  onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                  style={{ cursor: 'pointer' }}
                />
                <span style={{ fontSize: '14px', fontWeight: 500 }}>Set as default model</span>
              </label>
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '32px' }}>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setFormData({
                    name: '',
                    api_base: 'http://localhost:1234/v1',
                    api_key: 'not-needed',
                    model_name: '',
                    temperature: 0.7,
                    max_tokens: 2000,
                    top_p: 0.9,
                    is_default: false,
                  });
                }}
                style={{
                  padding: '10px 20px',
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'transparent',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  transition: 'all 0.2s'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={!formData.name || !formData.api_base || !formData.model_name}
                className="new-chat-btn"
                style={{
                  width: 'auto',
                  padding: '10px 20px',
                  opacity: (!formData.name || !formData.api_base || !formData.model_name) ? 0.5 : 1
                }}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
