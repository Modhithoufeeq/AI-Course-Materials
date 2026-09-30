import React from 'react';
import { ShieldAlert, ShieldCheck, Shield, AlertTriangle, FileText, Info } from 'lucide-react';
import { getOriginalityBadge } from '../../utils/statusBadges';

export const OriginalityMeter = ({ originalityReport }) => {
  if (!originalityReport) {
    return (
      <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        Originality check pending.
      </div>
    );
  }

  const { similarity_percentage, risk_level, status_label, match_summary, matches_json, disclaimer } = originalityReport;
  const badge = getOriginalityBadge(risk_level);

  const getRiskIcon = () => {
    switch (risk_level?.toLowerCase()) {
      case 'high':
        return <ShieldAlert size={26} color="var(--danger)" />;
      case 'medium':
      case 'moderate':
        return <AlertTriangle size={26} color="var(--warning)" />;
      case 'low':
      default:
        return <ShieldCheck size={26} color="var(--success)" />;
    }
  };

  const matches = matches_json || [];

  return (
    <div
      style={{
        padding: '1.5rem',
        borderRadius: 'var(--radius-lg)',
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-subtle)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      {/* Header Metric */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: risk_level === 'high' ? 'var(--danger-bg)' : risk_level === 'medium' ? 'var(--warning-bg)' : 'var(--success-bg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {getRiskIcon()}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Originality Index</h4>
              <span className={`badge ${badge.className}`}>{badge.label}</span>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Compared against peer corpus & course reference materials
            </span>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span
            style={{
              fontSize: '2rem',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              color: risk_level === 'high' ? 'var(--danger)' : risk_level === 'medium' ? 'var(--warning)' : 'var(--success)',
            }}
          >
            {similarity_percentage}%
          </span>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Similarity Overlap</div>
        </div>
      </div>

      {/* Summary Note */}
      {match_summary && (
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: 1.5 }}>
          {match_summary}
        </p>
      )}

      {/* Matches List */}
      {matches.length > 0 && (
        <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          <h5 style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Corpus Similarity Matches ({matches.length})
          </h5>
          {matches.map((m, idx) => (
            <div
              key={idx}
              style={{
                padding: '0.85rem 1rem',
                borderRadius: 'var(--radius-md)',
                backgroundColor: '#f8fafc',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  <FileText size={15} color="var(--primary-500)" />
                  {m.source_title}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>({m.student_name})</span>
                </div>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: m.similarity_percentage > 40 ? 'var(--danger)' : 'var(--warning)' }}>
                  {m.similarity_percentage}% match
                </span>
              </div>
              {m.overlap_snippet && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic', background: '#ffffff', padding: '6px 10px', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                  "{m.overlap_snippet}"
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Non-punitive AI Disclaimer */}
      <div
        style={{
          marginTop: '1.25rem',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.5rem',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          backgroundColor: '#f8fafc',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.775rem',
          color: 'var(--text-muted)',
        }}
      >
        <Info size={15} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--primary-500)' }} />
        <span>{disclaimer}</span>
      </div>
    </div>
  );
};
