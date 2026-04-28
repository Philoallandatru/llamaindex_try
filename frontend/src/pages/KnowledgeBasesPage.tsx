import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Plus, Trash2, RefreshCw, Database } from 'lucide-react';
import { knowledgeBaseApi, datasourceApi } from '../utils/api';
import '../styles/globals.css';

interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  datasource_ids: string[];
  status: string;
  document_count: number;
  created_at: string;
  updated_at: string;
}

interface DataSource {
  id: string;
  name: string;
  type: string;
}

export default function KnowledgeBasesPage() {
  const navigate = useNavigate();
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [datasources, setDatasources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    datasource_ids: [] as string[],
  });
  const [syncing, setSyncing] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [kbData, dsData] = await Promise.all([
        knowledgeBaseApi.list(),
        datasourceApi.list(),
      ]);
      setKnowledgeBases(kbData);
      setDatasources(dsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await knowledgeBaseApi.create(formData);
      setShowCreateModal(false);
      setFormData({ name: '', description: '', datasource_ids: [] });
      loadData();
    } catch (error) {
      console.error('Failed to create knowledge base:', error);
      alert('Failed to create knowledge base');
    }
  };

  const handleSync = async (id: string) => {
    try {
      setSyncing(id);
      await knowledgeBaseApi.sync(id);
      await loadData();
    } catch (error) {
      console.error('Failed to sync knowledge base:', error);
      alert('Failed to sync knowledge base');
    } finally {
      setSyncing(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this knowledge base?')) return;

    try {
      await knowledgeBaseApi.delete(id);
      loadData();
    } catch (error) {
      console.error('Failed to delete knowledge base:', error);
      alert('Failed to delete knowledge base');
    }
  };

  const toggleDatasource = (dsId: string) => {
    setFormData({
      ...formData,
      datasource_ids: formData.datasource_ids.includes(dsId)
        ? formData.datasource_ids.filter(id => id !== dsId)
        : [...formData.datasource_ids, dsId]
    });
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
          <div className="conversation-item active" onClick={() => navigate('/knowledge')}>
            Knowledge Base
          </div>
          <div className="conversation-item" onClick={() => navigate('/models')}>
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
                  Knowledge Bases
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                  Organize your data sources into searchable knowledge bases
                </p>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="new-chat-btn"
                style={{ width: 'auto', padding: '12px 24px' }}
              >
                <Plus size={18} />
                <span>Create Knowledge Base</span>
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
            {!loading && knowledgeBases.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon"><BookOpen size={64} /></div>
                <h2 className="empty-state-title">No knowledge bases yet</h2>
                <p className="empty-state-subtitle">
                  Create your first knowledge base to organize and search your documents
                </p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="new-chat-btn"
                  style={{ marginTop: '24px', width: 'auto', padding: '12px 24px' }}
                >
                  <Plus size={18} />
                  <span>Create Knowledge Base</span>
                </button>
              </div>
            )}

            {/* Knowledge Bases Grid */}
            {!loading && knowledgeBases.length > 0 && (
              <div style={{ display: 'grid', gap: '16px' }}>
                {knowledgeBases.map((kb) => (
                  <div
                    key={kb.id}
                    className="source-card"
                    style={{ cursor: 'default' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                          <div style={{ color: 'var(--accent)' }}>
                            <BookOpen size={20} />
                          </div>
                          <h3 className="source-title" style={{ margin: 0 }}>{kb.name}</h3>
                        </div>
                        {kb.description && (
                          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                            {kb.description}
                          </p>
                        )}
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                          {kb.document_count} documents • {kb.datasource_ids.length} data source(s)
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          Created {new Date(kb.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => handleSync(kb.id)}
                          disabled={syncing === kb.id}
                          style={{
                            padding: '8px 16px',
                            backgroundColor: 'var(--accent)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: syncing === kb.id ? 'not-allowed' : 'pointer',
                            fontSize: '13px',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            opacity: syncing === kb.id ? 0.6 : 1,
                            transition: 'all 0.2s'
                          }}
                        >
                          <RefreshCw size={14} className={syncing === kb.id ? 'spinning' : ''} />
                          {syncing === kb.id ? 'Syncing...' : 'Sync'}
                        </button>
                        <button
                          onClick={() => handleDelete(kb.id)}
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
            boxShadow: 'var(--shadow-xl)',
            border: '1px solid var(--border-color)'
          }}>
            <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '24px' }}>
              Create Knowledge Base
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
                placeholder="My Knowledge Base"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="message-input"
                style={{
                  padding: '12px 16px',
                  border: '1.5px solid var(--border-color)',
                  borderRadius: '10px',
                  backgroundColor: 'var(--input-bg)',
                  minHeight: '80px'
                }}
                placeholder="Optional description"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Select Data Sources
              </label>
              {datasources.length === 0 ? (
                <div style={{
                  padding: '16px',
                  backgroundColor: 'var(--bg-secondary)',
                  borderRadius: '8px',
                  fontSize: '13px',
                  color: 'var(--text-secondary)',
                  textAlign: 'center'
                }}>
                  No data sources available. Create one first.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {datasources.map((ds) => (
                    <label
                      key={ds.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '12px',
                        backgroundColor: formData.datasource_ids.includes(ds.id) ? 'var(--bg-tertiary)' : 'var(--bg-secondary)',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        border: '1.5px solid',
                        borderColor: formData.datasource_ids.includes(ds.id) ? 'var(--accent)' : 'transparent',
                        transition: 'all 0.2s'
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={formData.datasource_ids.includes(ds.id)}
                        onChange={() => toggleDatasource(ds.id)}
                        style={{ cursor: 'pointer' }}
                      />
                      <Database size={16} style={{ color: 'var(--text-secondary)' }} />
                      <span style={{ fontSize: '14px', fontWeight: 500 }}>{ds.name}</span>
                      <span style={{
                        marginLeft: 'auto',
                        padding: '2px 8px',
                        backgroundColor: 'var(--bg-primary)',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        color: 'var(--text-muted)'
                      }}>
                        {ds.type}
                      </span>
                    </label>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '32px' }}>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setFormData({ name: '', description: '', datasource_ids: [] });
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
                disabled={!formData.name || formData.datasource_ids.length === 0}
                className="new-chat-btn"
                style={{
                  width: 'auto',
                  padding: '10px 20px',
                  opacity: (!formData.name || formData.datasource_ids.length === 0) ? 0.5 : 1
                }}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spinning {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}
