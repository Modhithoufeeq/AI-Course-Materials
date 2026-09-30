import React from 'react';

export const Card = ({ title, subtitle, action, children, className = '', style = {}, ...props }) => {
  return (
    <div className={`card ${className}`} style={style} {...props}>
      {(title || action) && (
        <div className="card-header">
          <div>
            {title && <h3 className="card-title">{title}</h3>}
            {subtitle && <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
