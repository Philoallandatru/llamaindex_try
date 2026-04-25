import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import { analysisApi } from '../utils/api';
import '../styles/globals.css';

interface AnalysisSource {
  source_id: string;
  title: string;
  snippet: string;
  score: number;
  source_type: string;
}

interface RelatedIssue {
  issue_key: string;
  summary: string;
  status: string;
  link_type: string;
  url?: string;
}

interface AnalysisResult {
  issue_key: string;
  issue_summary: string;
  issue_description: string;
  analysis: string;
  sources: AnalysisSource[];
  related_issues: RelatedIssue[];
  timestamp: string;
  depth: string;
}

export default function AnalysisPage() {
  const { issueKey } = useParams<{ issueKey: string }>();
  const navigate = useNavigate();
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  // Try to load saved analysis first
  const { data: savedAnalysis } = useQuery({
    queryKey: ['savedAnalysis', issueKey],
    queryFn: () => analysisApi.getSavedAnalysis(issueKey!),
    enabled: !!issueKey,
    retry: false,
  });

  // Analyze issue mutation
  const analyzeMutation = useMutation({
    mutationFn: (key: string) => analysisApi.analyzeIssue(key, 'deep', true, true),
    onSuccess: (data) => {
      setAnalysisResult(data);
    },
  });

  useEffect(() => {
    if (savedAnalysis) {
      // Convert saved analysis format to AnalysisResult format
      setAnalysisResult({
        issue_key: savedAnalysis.issue_key,
        issue_summary: savedAnalysis.metadata?.issue_summary || issueKey || '',
        issue_description: savedAnalysis.metadata?.issue_description || '',
        analysis: savedAnalysis.analysis,
        sources: savedAnalysis.sources || [],
        related_issues: savedAnalysis.related_issues || [],
        timestamp: savedAnalysis.metadata?.timestamp || '',
        depth: savedAnalysis.metadata?.depth || 'deep',
      });
    } else if (issueKey && !analyzeMutation.isPending && !analysisResult) {
      // No saved analysis, start new analysis
      analyzeMutation.mutate(issueKey);
    }
  }, [savedAnalysis, issueKey]);

  if (!issueKey) {
    return <div>Invalid issue key</div>;
  }

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
          <div
            className="conversation-item active"
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
      </div>

      {/* Main Panel */}
      <div className="main-panel">
        <div className="chat-container">
          {/* Back Button */}
          <button
            onClick={() => navigate('/issues')}
            style={{
              padding: '8px 16px',
              backgroundColor: 'transparent',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              marginBottom: '16px',
              color: 'var(--text-primary)',
            }}
          >
            ← 返回列表
          </button>

          {/* Loading State */}
          {analyzeMutation.isPending && !analysisResult && (
            <div style={{ textAlign: 'center', padding: '60px' }}>
              <div className="typing-indicator" style={{ justifyContent: 'center' }}>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
              <div style={{ marginTop: '16px', color: 'var(--text-secondary)' }}>
                正在分析 {issueKey}...
              </div>
            </div>
          )}

          {/* Error State */}
          {analyzeMutation.isError && (
            <div style={{
              padding: '20px',
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              borderRadius: '8px',
              color: '#c00',
            }}>
              分析失败: {(analyzeMutation.error as Error).message}
            </div>
          )}

          {/* Analysis Result */}
          {analysisResult && (
            <div>
              {/* Issue Header */}
              <div style={{
                padding: '20px',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '8px',
                marginBottom: '24px',
              }}>
                <h1 style={{ fontSize: '24px', marginBottom: '8px' }}>
                  {analysisResult.issue_key}
                </h1>
                <h2 style={{ fontSize: '18px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                  {analysisResult.issue_summary}
                </h2>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  分析时间: {new Date(analysisResult.timestamp).toLocaleString('zh-CN')} |
                  深度: {analysisResult.depth === 'deep' ? '深度分析' : '快速分析'}
                </div>
              </div>

              {/* Issue Description */}
              {analysisResult.issue_description && (
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Issue 描述</h3>
                  <div style={{
                    padding: '16px',
                    backgroundColor: 'var(--bg-secondary)',
                    borderRadius: '8px',
                    whiteSpace: 'pre-wrap',
                    fontSize: '14px',
                    lineHeight: '1.6',
                  }}>
                    {analysisResult.issue_description}
                  </div>
                </div>
              )}

              {/* Analysis */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>深度分析</h3>
                <div style={{
                  padding: '20px',
                  backgroundColor: 'var(--bg-secondary)',
                  borderRadius: '8px',
                  fontSize: '14px',
                  lineHeight: '1.8',
                }}>
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => <h1 style={{ fontSize: '20px', marginTop: '16px', marginBottom: '12px' }}>{children}</h1>,
                      h2: ({ children }) => <h2 style={{ fontSize: '18px', marginTop: '16px', marginBottom: '10px' }}>{children}</h2>,
                      h3: ({ children }) => <h3 style={{ fontSize: '16px', marginTop: '12px', marginBottom: '8px' }}>{children}</h3>,
                      p: ({ children }) => <p style={{ marginBottom: '12px' }}>{children}</p>,
                      ul: ({ children }) => <ul style={{ marginLeft: '20px', marginBottom: '12px' }}>{children}</ul>,
                      ol: ({ children }) => <ol style={{ marginLeft: '20px', marginBottom: '12px' }}>{children}</ol>,
                      li: ({ children }) => <li style={{ marginBottom: '4px' }}>{children}</li>,
                      code: ({ children }) => <code style={{ backgroundColor: 'var(--bg-tertiary)', padding: '2px 6px', borderRadius: '4px', fontSize: '13px' }}>{children}</code>,
                      pre: ({ children }) => <pre style={{ backgroundColor: 'var(--bg-tertiary)', padding: '12px', borderRadius: '6px', overflow: 'auto', marginBottom: '12px' }}>{children}</pre>,
                      blockquote: ({ children }) => <blockquote style={{ borderLeft: '3px solid var(--accent)', paddingLeft: '12px', marginLeft: '0', marginBottom: '12px', color: 'var(--text-secondary)' }}>{children}</blockquote>,
                    }}
                  >
                    {analysisResult.analysis}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Related Issues */}
              {analysisResult.related_issues && analysisResult.related_issues.length > 0 && (
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>关联 Issues</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {analysisResult.related_issues.map((related) => (
                      <div
                        key={related.issue_key}
                        style={{
                          padding: '12px',
                          backgroundColor: 'var(--bg-secondary)',
                          borderRadius: '6px',
                          fontSize: '14px',
                        }}
                      >
                        <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                          {related.url ? (
                            <a href={related.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>
                              {related.issue_key}
                            </a>
                          ) : (
                            related.issue_key
                          )}
                          <span style={{ marginLeft: '8px', color: 'var(--text-secondary)', fontWeight: 'normal' }}>
                            ({related.link_type})
                          </span>
                        </div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                          {related.summary} - <em>{related.status}</em>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sources */}
              {analysisResult.sources && analysisResult.sources.length > 0 && (
                <div>
                  <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>参考文档</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {analysisResult.sources.map((source, idx) => (
                      <div
                        key={source.source_id}
                        style={{
                          padding: '16px',
                          backgroundColor: 'var(--bg-secondary)',
                          borderRadius: '8px',
                          fontSize: '14px',
                        }}
                      >
                        <div style={{ fontWeight: '600', marginBottom: '8px' }}>
                          {idx + 1}. {source.title}
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                          类型: {source.source_type} | 相关度: {source.score.toFixed(2)}
                        </div>
                        <div style={{
                          padding: '12px',
                          backgroundColor: 'var(--bg-tertiary)',
                          borderRadius: '6px',
                          fontSize: '13px',
                          lineHeight: '1.6',
                          color: 'var(--text-secondary)',
                        }}>
                          {source.snippet}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
