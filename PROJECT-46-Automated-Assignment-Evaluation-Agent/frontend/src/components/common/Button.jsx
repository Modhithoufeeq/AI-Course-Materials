import React from 'react';

export const Button = ({
  children,
  variant = 'primary', // primary, secondary, success, danger
  size = 'md', // sm, md, lg
  icon: Icon,
  isLoading = false,
  disabled = false,
  className = '',
  ...props
}) => {
  const variantClass = `btn-${variant}`;
  const sizeClass = size !== 'md' ? `btn-${size}` : '';

  return (
    <button
      className={`btn ${variantClass} ${sizeClass} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
          <svg
            style={{ animation: 'spin 1s linear infinite', width: '16px', height: '16px' }}
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" strokeOpacity="0.25" />
            <path
              d="M12 2a10 10 0 0 1 10 10"
              stroke="currentColor"
              strokeWidth="4"
              strokeLinecap="round"
            />
          </svg>
          Loading...
        </span>
      ) : (
        <>
          {Icon && <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />}
          {children}
        </>
      )}
    </button>
  );
};
