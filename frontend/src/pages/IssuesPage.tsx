import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analysisApi } from '../utils/api';
import { useNavigate } from 'react-router-dom';
import '../styles/globals.css';

interface AnalyzedIssue {
  issue_key: string;
  timestamp: string;
  depth: string;
  sources_count: number;
  related_issues_count: number;
}

export default function IssuesPage() {
  const navigate = useNavigate();
  const [manualIssueKey, setManualIssueKey] = useState('');

  // Fetch analyzed issues
  const { data: analyzedIssues, isLoading } = useQuery({
    queryKey: ['analyzedIssues'],
    queryFn: () => analysisApi.listAnalyzedIssues(),
  });

  const handleAnalyzeManual = () => {
    if (manualIssueKey.trim()) {
      navigate(`/analysis/${manualIssueKey.trim()}`);
    }
  };

  const handleViewAnalysis = (issueKey: string) => {
    navigate(`/analysis/${issueKey}`);
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h2 style={{ color: 'var(--sidebar-text)', fontSize: '18px', marginBottom: '16px' }}>
            SSD Knowledge Portal
          </h2>
        </div>
        <div className="conversation-list">
          <div
            className="conversation-item"
            onClick={() => navigate('/')}
          >
            💬 Chat
          </div>
          <div className="conversation-item active">
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
      </div>

      {/* Main Panel */}
      <div className="main-panel">
        <div className="chat-container">
          <h1 style={{ fontSize: '24px', marginBottom: '24px' }}>Issue 深度分析</h1>

          {/* Manual Analysis Input */}
          <div style={{
            padding: '20px',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: '8px',
            marginBottom: '32px',
          }}>
            <h2 style={{ fontSize: '18px', marginBottom: '12px' }}>分析新 Issue</h2>
            <div style={{ display: 'flex', gap: '12px' }}>
              <input
                type="text"
                value={manualIssueKey}
                onChange={(e) => setManualIssueKey(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAnalyzeManual()}
                placeholder="输入 Issue Key (例如: PROJ-123)"
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  backgroundColor: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                }}
              />
              <button
                onClick={handleAnalyzeManual}
                disabled={!manualIssueKey.trim()}
                style={{
                  padding: '12px 24px',
                  backgroundColor: 'var(--accent)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: manualIssueKey.trim() ? 'pointer' : 'not-allowed',
                  fontSize: '14px',
                  fontWeight: '500',
                  opacity: manualIssueKey.trim() ? 1 : 0.5,
                }}
              >
                开始分析
              </button>
            </div>
          </div>

          {/* Analyzed Issues List */}
          <div>
            <h2 style={{ fontSize: '18px', marginBottom: '16px' }}>已分析的 Issues</h2>

            {isLoading && (
              <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                加载中...
              </div>
            )}

            {!isLoading && analyzedIssues && analyzedIssues.length === 0 && (
              <div style={{
                textAlign: 'center',
                padding: '40px',
                color: 'var(--text-secondary)',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '8px',
              }}>
                暂无已分析的 Issues
              </div>
            )}

            {!isLoading && analyzedIssues && analyzedIssues.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {analyzedIssues.map((issue: AnalyzedIssue) => (
                  <div
                    key={issue.issue_key}
                    onClick={() => handleViewAnalysis(issue.issue_key)}
                    style={{
                      padding: '16px',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s',
                      border: '1px solid var(--border-color)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--bg-secondary)';
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '4px' }}>
                          {issue.issue_key}
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                          分析时间: {new Date(issue.timestamp).toLocaleString('zh-CN')}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '16px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                        <span>深度: {issue.depth === 'deep' ? '深度' : '快速'}</span>
                        <span>文档: {issue.sources_count}</span>
                        <span>关联: {issue.related_issues_count}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
