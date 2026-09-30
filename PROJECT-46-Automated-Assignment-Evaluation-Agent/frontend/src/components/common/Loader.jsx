import React from 'react';

export const Loader = ({ message = 'Loading...', size = 'md' }) => {
  const sizePx = size === 'sm' ? 24 : size === 'lg' ? 48 : 36;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 1rem', gap: '1rem' }}>
      <svg
        style={{
          width: `${sizePx}px`,
          height: `${sizePx}px`,
          animation: 'spin 1s linear infinite',
          color: 'var(--primary-500)',
        }}
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.2" />
        <path
          d="M12 2a10 10 0 0 1 10 10"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      {message && <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>{message}</p>}
    </div>
  );
};
