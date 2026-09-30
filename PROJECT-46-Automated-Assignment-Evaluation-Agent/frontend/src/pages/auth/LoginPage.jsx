import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, GraduationCap, School, ArrowRight, Lock, Mail } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please enter both email and password.');
      return;
    }

    setIsLoading(true);
    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.full_name}!`);
      if (user.role === 'teacher' || user.role === 'admin') {
        navigate('/teacher/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid email or password.';
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickDemo = async (role) => {
    setIsLoading(true);
    try {
      const demoEmail = role === 'teacher' ? 'teacher@evalagent.com' : 'student1@evalagent.com';
      const user = await login(demoEmail, 'password123');
      toast.success(`Logged in as ${user.full_name} (${user.role})`);
      if (user.role === 'teacher' || user.role === 'admin') {
        navigate('/teacher/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (err) {
      toast.error('Could not log into demo account. Please ensure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        backgroundColor: '#ffffff',
      }}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '440px',
          padding: '2.5rem',
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          boxShadow: 'var(--shadow-xl)',
          borderRadius: 'var(--radius-lg)',
        }}
      >
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--primary-gradient)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              boxShadow: 'var(--accent-glow)',
              marginBottom: '1rem',
            }}
          >
            <Sparkles size={24} />
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)' }}>AutoEval AI</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Automated Rubric Evaluation & Feedback SaaS
          </p>
        </div>

        {/* 1-Click Demo Buttons */}
        <div style={{ marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            1-Click Demo Access
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
            <Button
              type="button"
              variant="secondary"
              icon={School}
              onClick={() => handleQuickDemo('teacher')}
              disabled={isLoading}
              size="sm"
              style={{ justifyContent: 'center' }}
            >
              Teacher Demo
            </Button>
            <Button
              type="button"
              variant="secondary"
              icon={GraduationCap}
              onClick={() => handleQuickDemo('student')}
              disabled={isLoading}
              size="sm"
              style={{ justifyContent: 'center' }}
            >
              Student Demo
            </Button>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: '1.25rem 0' }}>
          <div style={{ flex: 1, height: '1px', background: 'var(--border-subtle)' }} />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>OR SIGN IN</span>
          <div style={{ flex: 1, height: '1px', background: 'var(--border-subtle)' }} />
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <Input
            label="Email Address"
            type="email"
            placeholder="you@institution.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            Sign In to Portal
          </Button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ fontWeight: 600, color: 'var(--primary-500)' }}>
            Register here
          </Link>
        </div>
      </div>
    </div>
  );
};
