import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import { reportsApi } from '../utils/api';
import '../styles/globals.css';

interface DailyReport {
  report_id: string;
  date: string;
  mode: 'quick' | 'full';
  summary: {
    total_issues: number;
    by_status: Record<string, number>;
    by_priority: Record<string, number>;
    by_assignee: Record<string, number>;
  };
  issues: Array<{
    key: string;
    summary: string;
    status: string;
    priority: string;
    assignee: string;
    updated: string;
  }>;
  insights?: string;
  recommendations?: string[];
  timestamp: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  current_step?: string;
}

export default function ReportsPage() {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [reportMode, setReportMode] = useState<'quick' | 'full'>('quick');
  const [currentReport, setCurrentReport] = useState<DailyReport | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  // List saved reports
  const { data: savedReports } = useQuery({
    queryKey: ['savedReports'],
    queryFn: () => reportsApi.listReports(),
    retry: false,
  });

  // Generate report mutation
  const generateMutation = useMutation({
    mutationFn: ({ date, mode }: { date: string; mode: 'quick' | 'full' }) =>
      reportsApi.generateReport(date, mode),
    onSuccess: (data) => {
      setCurrentReport(data);
      // Connect to WebSocket for real-time updates
      if (data.report_id && data.status === 'processing') {
        connectWebSocket(data.report_id);
      }
    },
  });

  const connectWebSocket = (reportId: string) => {
    const wsUrl = `ws://localhost:8000/ws/daily/${reportId}`;
    const websocket = new WebSocket(wsUrl);

    websocket.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setCurrentReport((prev) => (prev ? { ...prev, ...update } : null));
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket closed');
    };

    setWs(websocket);
  };

  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  const handleGenerate = () => {
    generateMutation.mutate({ date: selectedDate, mode: reportMode });
  };

  const handleLoadReport = (date: string) => {
    reportsApi.getSavedReport(date).then((data) => {
      setCurrentReport(data);
      setSelectedDate(date);
    });
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
          <div className="conversation-item" onClick={() => navigate('/')}>
            💬 Chat
          </div>
          <div className="conversation-item" onClick={() => navigate('/issues')}>
            🔍 Issues Analysis
          </div>
          <div className="conversation-item active">
            📊 Daily Reports
          </div>
          <div className="conversation-item" onClick={() => navigate('/knowledge')}>
            📚 Knowledge Base
          </div>
        </div>

        {/* Saved Reports List */}
        {savedReports && savedReports.length > 0 && (
          <div style={{ marginTop: '24px', padding: '0 12px' }}>
            <h3 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              历史报告
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {savedReports.map((report: any) => (
                <div
                  key={report.date}
                  onClick={() => handleLoadReport(report.date)}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: selectedDate === report.date ? 'var(--accent)' : 'var(--bg-secondary)',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '13px',
                    color: selectedDate === report.date ? 'white' : 'var(--text-primary)',
                  }}
                >
                  {report.date}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Main Panel */}
      <div className="main-panel">
        <div className="chat-container">
          <h1 style={{ fontSize: '24px', marginBottom: '24px' }}>每日报告</h1>

          {/* Report Generation Form */}
          <div style={{
            padding: '20px',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: '8px',
            marginBottom: '24px',
          }}>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
              <div style={{ flex: '1', minWidth: '200px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px' }}>
                  日期
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ flex: '1', minWidth: '200px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px' }}>
                  报告模式
                </label>
                <select
                  value={reportMode}
                  onChange={(e) => setReportMode(e.target.value as 'quick' | 'full')}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    backgroundColor: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    fontSize: '14px',
                  }}
                >
                  <option value="quick">快速报告</option>
                  <option value="full">完整报告</option>
                </select>
              </div>

              <button
                onClick={handleGenerate}
                disabled={generateMutation.isPending}
                style={{
                  padding: '8px 24px',
                  backgroundColor: 'var(--accent)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: generateMutation.isPending ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  opacity: generateMutation.isPending ? 0.6 : 1,
                }}
              >
                {generateMutation.isPending ? '生成中...' : '生成报告'}
              </button>
            </div>
          </div>

          {/* Loading State */}
          {generateMutation.isPending && !currentReport && (
            <div style={{ textAlign: 'center', padding: '60px' }}>
              <div className="typing-indicator" style={{ justifyContent: 'center' }}>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
              <div style={{ marginTop: '16px', color: 'var(--text-secondary)' }}>
                正在生成报告...
              </div>
            </div>
          )}

          {/* Progress Indicator */}
          {currentReport && currentReport.status === 'processing' && (
            <div style={{
              padding: '20px',
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: '8px',
              marginBottom: '24px',
            }}>
              <div style={{ marginBottom: '12px', fontSize: '14px' }}>
                {currentReport.current_step || '处理中...'}
              </div>
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: 'var(--bg-tertiary)',
                borderRadius: '4px',
                overflow: 'hidden',
              }}>
                <div style={{
                  width: `${currentReport.progress || 0}%`,
                  height: '100%',
                  backgroundColor: 'var(--accent)',
                  transition: 'width 0.3s ease',
                }} />
              </div>
            </div>
          )}

          {/* Error State */}
          {generateMutation.isError && (
            <div style={{
              padding: '20px',
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              borderRadius: '8px',
              color: '#c00',
              marginBottom: '24px',
            }}>
              生成失败: {(generateMutation.error as Error).message}
            </div>
          )}

          {/* Report Display */}
          {currentReport && currentReport.status === 'completed' && (
            <div>
              {/* Report Header */}
              <div style={{
                padding: '20px',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '8px',
                marginBottom: '24px',
              }}>
                <h2 style={{ fontSize: '20px', marginBottom: '8px' }}>
                  {currentReport.date} 每日报告
                </h2>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  生成时间: {new Date(currentReport.timestamp).toLocaleString('zh-CN')} |
                  模式: {currentReport.mode === 'quick' ? '快速' : '完整'}
                </div>
              </div>

              {/* Summary Statistics */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>统计概览</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div style={{
                    padding: '16px',
                    backgroundColor: 'var(--bg-secondary)',
                    borderRadius: '8px',
                  }}>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                      总 Issues
                    </div>
                    <div style={{ fontSize: '24px', fontWeight: '600' }}>
                      {currentReport.summary.total_issues}
                    </div>
                  </div>

                  {Object.entries(currentReport.summary.by_status).map(([status, count]) => (
                    <div key={status} style={{
                      padding: '16px',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: '8px',
                    }}>
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                        {status}
                      </div>
                      <div style={{ fontSize: '24px', fontWeight: '600' }}>
                        {count}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Insights (Full mode only) */}
              {currentReport.insights && (
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>深度洞察</h3>
                  <div style={{
                    padding: '20px',
                    backgroundColor: 'var(--bg-secondary)',
                    borderRadius: '8px',
                    fontSize: '14px',
                    lineHeight: '1.8',
                  }}>
                    <ReactMarkdown>{currentReport.insights}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {currentReport.recommendations && currentReport.recommendations.length > 0 && (
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>建议</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {currentReport.recommendations.map((rec, idx) => (
                      <div key={idx} style={{
                        padding: '12px',
                        backgroundColor: 'var(--bg-secondary)',
                        borderRadius: '6px',
                        fontSize: '14px',
                      }}>
                        {idx + 1}. {rec}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Issues List */}
              <div>
                <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Issues 列表</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {currentReport.issues.map((issue) => (
                    <div key={issue.key} style={{
                      padding: '16px',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: '8px',
                      fontSize: '14px',
                    }}>
                      <div style={{ fontWeight: '600', marginBottom: '8px' }}>
                        {issue.key}: {issue.summary}
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                        状态: {issue.status} | 优先级: {issue.priority} |
                        负责人: {issue.assignee} | 更新: {new Date(issue.updated).toLocaleDateString('zh-CN')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
