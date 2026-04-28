import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Upload, RefreshCw, Trash2, Plus, FileText, Server, Cloud } from 'lucide-react';
import { datasourceApi } from '../utils/api';
import '../styles/globals.css';

interface DataSource {
  id: string;
  name: string;
  type: string;
  status: string;
  document_count: number;
  last_sync: string | null;
  created_at: string;
  updated_at: string;
}

export default function DataSourcesPage() {
  const navigate = useNavigate();
  const [datasources, setDatasources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedType, setSelectedType] = useState<'file' | 'jira' | 'confluence'>('file');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    file_paths: [] as string[],
  });
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadDatasources();
  }, []);

  const loadDatasources = async () => {
    try {
      setLoading(true);
      const data = await datasourceApi.list();
      setDatasources(data);
    } catch (error) {
      console.error('Failed to load datasources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    console.log('Starting upload for files:', files.map(f => ({ name: f.name, type: f.type, size: f.size })));
    setUploading(true);
    try {
      const uploadPromises = files.map(file => {
        console.log('Uploading file:', file.name);
        return datasourceApi.uploadFile(file);
      });
      const results = await Promise.all(uploadPromises);
      console.log('Upload results:', results);
      const filePaths = results.flatMap(r => r.file_paths || []);

      console.log('Uploaded file paths:', filePaths);
      setUploadedFiles(files);
      setFormData({ ...formData, file_paths: filePaths });
    } catch (error: any) {
      console.error('Failed to upload files:', error);
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      console.error('Error response headers:', error.response?.headers);
      alert(`Failed to upload files: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    } finally {
      setUploading(false);
    }
  };

  const handleCreate = async () => {
    setCreating(true);
    try {
      console.log('Creating datasource with data:', {
        name: formData.name,
        type: selectedType,
        description: formData.description,
        config: selectedType === 'file' ? { file_paths: formData.file_paths } : {}
      });

      await datasourceApi.create({
        name: formData.name,
        type: selectedType,
        description: formData.description,
        config: selectedType === 'file' ? { file_paths: formData.file_paths } : {}
      });

      setShowCreateModal(false);
      setFormData({ name: '', description: '', file_paths: [] });
      setUploadedFiles([]);
      loadDatasources();
    } catch (error) {
      console.error('Failed to create datasource:', error);
      alert(`Failed to create datasource: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setCreating(false);
    }
  };

  const handleSync = async (id: string) => {
    try {
      setSyncing(id);
      await datasourceApi.sync(id);
      await loadDatasources();
    } catch (error) {
      console.error('Failed to sync datasource:', error);
      alert('Failed to sync datasource');
    } finally {
      setSyncing(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this datasource?')) return;

    try {
      await datasourceApi.delete(id);
      loadDatasources();
    } catch (error) {
      console.error('Failed to delete datasource:', error);
      alert('Failed to delete datasource');
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'file': return <FileText size={20} />;
      case 'jira': return <Server size={20} />;
      case 'confluence': return <Cloud size={20} />;
      default: return <Database size={20} />;
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
          <div className="conversation-item active" onClick={() => navigate('/datasources')}>
            Data Sources
          </div>
          <div className="conversation-item" onClick={() => navigate('/knowledge')}>
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
                  Data Sources
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                  Manage your document sources and sync data
                </p>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="new-chat-btn"
                style={{ width: 'auto', padding: '12px 24px' }}
              >
                <Plus size={18} />
                <span>Add Data Source</span>
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
            {!loading && datasources.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon"><Database size={64} /></div>
                <h2 className="empty-state-title">No data sources yet</h2>
                <p className="empty-state-subtitle">
                  Add your first data source to start building your knowledge base
                </p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="new-chat-btn"
                  style={{ marginTop: '24px', width: 'auto', padding: '12px 24px' }}
                >
                  <Plus size={18} />
                  <span>Add Data Source</span>
                </button>
              </div>
            )}

            {/* Data Sources Grid */}
            {!loading && datasources.length > 0 && (
              <div style={{ display: 'grid', gap: '16px' }}>
                {datasources.map((ds) => (
                  <div
                    key={ds.id}
                    className="source-card"
                    style={{ cursor: 'default' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                          <div style={{ color: 'var(--accent)' }}>
                            {getTypeIcon(ds.type)}
                          </div>
                          <h3 className="source-title" style={{ margin: 0 }}>{ds.name}</h3>
                          <span style={{
                            padding: '2px 8px',
                            backgroundColor: 'var(--bg-tertiary)',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            color: 'var(--text-secondary)'
                          }}>
                            {ds.type}
                          </span>
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                          {ds.document_count} documents
                          {ds.last_sync && ` • Last synced ${new Date(ds.last_sync).toLocaleString()}`}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          Created {new Date(ds.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => handleSync(ds.id)}
                          disabled={syncing === ds.id}
                          style={{
                            padding: '8px 16px',
                            backgroundColor: 'var(--accent)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: syncing === ds.id ? 'not-allowed' : 'pointer',
                            fontSize: '13px',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            opacity: syncing === ds.id ? 0.6 : 1,
                            transition: 'all 0.2s'
                          }}
                        >
                          <RefreshCw size={14} className={syncing === ds.id ? 'spinning' : ''} />
                          {syncing === ds.id ? 'Syncing...' : 'Sync'}
                        </button>
                        <button
                          onClick={() => handleDelete(ds.id)}
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
              Add Data Source
            </h2>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Type
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value as any)}
                className="config-select"
              >
                <option value="file">File</option>
                <option value="jira">Jira</option>
                <option value="confluence">Confluence</option>
              </select>
            </div>

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
                placeholder="My Data Source"
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

            {selectedType === 'file' && (
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  Upload Files
                </label>
                <div style={{
                  border: '2px dashed var(--border-color)',
                  borderRadius: '10px',
                  padding: '24px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--accent)'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
                >
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    multiple
                    accept=".pdf,.doc,.docx,.txt,.md"
                    style={{ display: 'none' }}
                    id="file-upload"
                    disabled={uploading}
                  />
                  <label htmlFor="file-upload" style={{ cursor: uploading ? 'not-allowed' : 'pointer' }}>
                    <Upload size={32} style={{ color: 'var(--text-muted)', marginBottom: '8px' }} />
                    <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                      {uploading ? 'Uploading...' : 'Click to upload or drag and drop'}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                      PDF, DOC, DOCX, TXT, MD
                    </div>
                  </label>
                </div>
                {uploading && (
                  <div style={{ marginTop: '12px', textAlign: 'center' }}>
                    <div className="typing-indicator" style={{ justifyContent: 'center' }}>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                )}
                {!uploading && uploadedFiles.length > 0 && (
                  <div style={{ marginTop: '12px', fontSize: '13px', color: 'var(--accent)' }}>
                    ✓ {uploadedFiles.length} file(s) uploaded
                  </div>
                )}
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '32px' }}>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setFormData({ name: '', description: '', file_paths: [] });
                  setUploadedFiles([]);
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
                disabled={creating || !formData.name || (selectedType === 'file' && formData.file_paths.length === 0)}
                className="new-chat-btn"
                style={{
                  width: 'auto',
                  padding: '10px 20px',
                  opacity: (creating || !formData.name || (selectedType === 'file' && formData.file_paths.length === 0)) ? 0.5 : 1,
                  cursor: creating ? 'not-allowed' : 'pointer'
                }}
              >
                {creating ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                    Creating...
                  </span>
                ) : (
                  'Create'
                )}
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
