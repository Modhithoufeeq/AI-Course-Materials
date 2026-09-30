import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Home, ArrowLeft } from 'lucide-react';
import { Button } from '../components/common/Button';

export const NotFoundPage = () => {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        textAlign: 'center',
        backgroundColor: '#ffffff',
      }}
    >
      <div style={{ maxWidth: '440px' }}>
        <h1 style={{ fontSize: '5rem', fontWeight: 900, color: 'var(--primary-500)', lineHeight: 1 }}>404</h1>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '1rem 0 0.5rem', color: 'var(--text-primary)' }}>Page Not Found</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
          The page or evaluation report you are looking for does not exist or has been moved.
        </p>
        <Link to="/">
          <Button variant="primary" icon={Home}>
            Return to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
};
