import React from 'react';

export const Input = ({
  label,
  error,
  helperText,
  type = 'text',
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="form-group">
      {label && <label htmlFor={inputId} className="form-label">{label}</label>}
      <input
        id={inputId}
        type={type}
        className={`form-input ${error ? 'border-danger' : ''} ${className}`}
        style={error ? { borderColor: 'var(--danger)' } : {}}
        {...props}
      />
      {error && <span style={{ fontSize: '0.75rem', color: 'var(--danger)', marginTop: '0.2rem' }}>{error}</span>}
      {helperText && !error && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{helperText}</span>}
    </div>
  );
};

export const Textarea = ({
  label,
  error,
  helperText,
  className = '',
  id,
  rows = 4,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="form-group">
      {label && <label htmlFor={inputId} className="form-label">{label}</label>}
      <textarea
        id={inputId}
        rows={rows}
        className={`form-textarea ${error ? 'border-danger' : ''} ${className}`}
        style={error ? { borderColor: 'var(--danger)' } : {}}
        {...props}
      />
      {error && <span style={{ fontSize: '0.75rem', color: 'var(--danger)', marginTop: '0.2rem' }}>{error}</span>}
      {helperText && !error && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{helperText}</span>}
    </div>
  );
};
