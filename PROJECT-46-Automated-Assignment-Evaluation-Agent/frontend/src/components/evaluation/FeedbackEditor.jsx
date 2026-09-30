import React from 'react';
import { Sparkles, CheckCircle2, AlertCircle, ArrowUpRight, MessageSquare, Lightbulb } from 'lucide-react';

export const FeedbackEditor = ({
  feedback,
  teacherCustomFeedback = '',
  isEditable = false,
  onTeacherFeedbackChange = null,
}) => {
  if (!feedback) {
    return (
      <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        Personalized feedback synthesis pending.
      </div>
    );
  }

  const { executive_summary, strengths_json, weaknesses_json, improvements_json, action_items_json } = feedback;
  const strengths = strengths_json || [];
  const weaknesses = weaknesses_json || [];
  const improvements = improvements_json || [];
  const actionItems = action_items_json || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Executive Summary */}
      <div
        style={{
          padding: '1.25rem',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-xs)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
          <Sparkles size={18} color="var(--primary-500)" />
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Executive Evaluation Summary</h4>
        </div>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {executive_summary}
        </p>
      </div>

      {/* Grid of Strengths & Areas for Improvement */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {/* Strengths */}
        <div
          style={{
            padding: '1.25rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: '#f0fdf4',
            border: '1px solid #bbf7d0',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <CheckCircle2 size={18} color="var(--success)" />
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#14532d' }}>Key Strengths</h4>
          </div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {strengths.map((item, i) => (
              <li
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                  fontSize: '0.85rem',
                  color: '#166534',
                  lineHeight: 1.4,
                }}
              >
                <span style={{ color: 'var(--success)', fontWeight: 700 }}>•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Areas to Improve */}
        <div
          style={{
            padding: '1.25rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: '#fffbeb',
            border: '1px solid #fde68a',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <Lightbulb size={18} color="var(--warning)" />
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#78350f' }}>Areas for Growth</h4>
          </div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {improvements.map((item, i) => (
              <li
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                  fontSize: '0.85rem',
                  color: '#92400e',
                  lineHeight: 1.4,
                }}
              >
                <span style={{ color: 'var(--warning)', fontWeight: 700 }}>•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Action Items */}
      {actionItems.length > 0 && (
        <div
          style={{
            padding: '1.25rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: '#ffffff',
            border: '1px solid var(--border-subtle)',
            boxShadow: 'var(--shadow-xs)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
            <ArrowUpRight size={18} color="var(--info)" />
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>Recommended Action Steps</h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {actionItems.map((item, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  fontSize: '0.85rem',
                  color: 'var(--text-primary)',
                  padding: '0.5rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: '#f0f9ff',
                  border: '1px solid #e0f2fe',
                }}
              >
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--info)' }} />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Teacher Custom Feedback / Notes */}
      <div
        style={{
          padding: '1.25rem',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-xs)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
          <MessageSquare size={18} color="var(--purple)" />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>Instructor Comments</h4>
        </div>
        {isEditable ? (
          <textarea
            rows={3}
            className="form-textarea"
            placeholder="Add optional personalized instructor notes or instructions before publishing..."
            value={teacherCustomFeedback}
            onChange={(e) => onTeacherFeedbackChange && onTeacherFeedbackChange(e.target.value)}
            style={{ width: '100%' }}
          />
        ) : (
          <p style={{ fontSize: '0.9rem', color: teacherCustomFeedback ? 'var(--text-primary)' : 'var(--text-muted)', fontStyle: teacherCustomFeedback ? 'normal' : 'italic' }}>
            {teacherCustomFeedback || 'No additional instructor notes added.'}
          </p>
        )}
      </div>
    </div>
  );
};
