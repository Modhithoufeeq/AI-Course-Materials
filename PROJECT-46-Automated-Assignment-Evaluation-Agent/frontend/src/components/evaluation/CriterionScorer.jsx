import React from 'react';
import { Quote, CheckCircle2, AlertCircle } from 'lucide-react';
import { formatPercentage } from '../../utils/formatters';

export const CriterionScorer = ({
  criterionScores = [],
  isEditable = false,
  onScoreChange = null,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {criterionScores.map((c) => {
        const percentage = (c.score / c.max_points) * 100;
        const isHigh = percentage >= 80;
        const isMed = percentage >= 60 && percentage < 80;

        return (
          <div
            key={c.id || c.criterion_id}
            style={{
              padding: '1.25rem',
              borderRadius: 'var(--radius-lg)',
              backgroundColor: '#ffffff',
              border: '1px solid var(--border-subtle)',
              boxShadow: 'var(--shadow-xs)',
            }}
          >
            {/* Header: Name and Points */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {c.criterion_name}
                </h4>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Max points: {c.max_points} pts
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {isEditable ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      max={c.max_points}
                      value={c.score}
                      onChange={(e) => onScoreChange && onScoreChange(c.criterion_id, parseFloat(e.target.value) || 0)}
                      style={{
                        width: '70px',
                        padding: '5px 8px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: '#ffffff',
                        border: '1px solid var(--primary-500)',
                        color: 'var(--text-primary)',
                        fontWeight: 700,
                        textAlign: 'center',
                        boxShadow: 'var(--shadow-xs)',
                      }}
                    />
                    <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>/ {c.max_points}</span>
                  </div>
                ) : (
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: isHigh ? 'var(--success)' : isMed ? 'var(--warning)' : 'var(--danger)' }}>
                      {c.score}
                    </span>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                      {' '}/ {c.max_points} pts
                    </span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                      ({formatPercentage(percentage)})
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Score Visual Bar */}
            <div className="progress-bar-container" style={{ marginBottom: '0.85rem' }}>
              <div
                className="progress-bar-fill"
                style={{
                  width: `${Math.min(100, Math.max(0, percentage))}%`,
                  background: isHigh
                    ? 'linear-gradient(90deg, #059669, #10b981)'
                    : isMed
                    ? 'linear-gradient(90deg, #d97706, #f59e0b)'
                    : 'linear-gradient(90deg, #dc2626, #ef4444)',
                }}
              />
            </div>

            {/* AI Evaluator Rationale */}
            {c.rationale && (
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', lineHeight: 1.5 }}>
                {c.rationale}
              </p>
            )}

            {/* Extracted Evidence Quote Snippet */}
            {c.evidence_quote && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                  padding: '0.65rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: '#eef2ff',
                  borderLeft: '3px solid var(--primary-500)',
                  fontSize: '0.825rem',
                  color: '#3730a3',
                  fontStyle: 'italic',
                }}
              >
                <Quote size={14} style={{ flexShrink: 0, marginTop: '2px', opacity: 0.8 }} />
                <span>"{c.evidence_quote}"</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
