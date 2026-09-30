import React from 'react';
import {
  CheckCircle2,
  Clock,
  Cpu,
  FileCheck,
  Search,
  Sliders,
  Sparkles,
  AlertCircle,
  ShieldCheck,
} from 'lucide-react';

export const AgentLogViewer = ({ logs = [] }) => {
  if (!logs || logs.length === 0) {
    return (
      <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No agent decision logs recorded yet.
      </div>
    );
  }

  const getStepIcon = (stepName) => {
    switch (stepName) {
      case 'DOCUMENT_VALIDATION':
        return <FileCheck size={16} color="#0284c7" />;
      case 'RUBRIC_ANALYSIS':
        return <Sliders size={16} color="#7c3aed" />;
      case 'RAG_RETRIEVAL':
        return <Search size={16} color="#4f46e5" />;
      case 'CRITERION_EVALUATION':
        return <Cpu size={16} color="#db2777" />;
      case 'ORIGINALITY_ANALYSIS':
        return <ShieldCheck size={16} color="#d97706" />;
      case 'SCORING_ARITHMETIC':
        return <CheckCircle2 size={16} color="#059669" />;
      case 'FEEDBACK_SYNTHESIS':
        return <Sparkles size={16} color="#6366f1" />;
      default:
        return <Clock size={16} color="var(--text-muted)" />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)' }}>
          <Cpu size={18} color="var(--primary-500)" />
          Agentic Execution Audit Trail
        </h4>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
          {logs.length} Orchestrated Steps
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
        {logs.map((log, index) => (
          <div
            key={log.id || index}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              backgroundColor: '#f8fafc',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div style={{ marginTop: '2px' }}>{getStepIcon(log.step_name)}</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {log.step_name.replace(/_/g, ' ')}
                </span>
                <span
                  style={{
                    fontSize: '0.7rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    backgroundColor: '#e2e8f0',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontWeight: 600,
                  }}
                >
                  {log.execution_time_ms}ms
                </span>
              </div>
              <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                {log.details}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
