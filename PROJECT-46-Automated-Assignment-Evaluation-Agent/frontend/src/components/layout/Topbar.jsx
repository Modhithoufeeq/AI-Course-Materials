import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Sparkles, ShieldCheck, ChevronRight, UserCheck } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';

export const Topbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, login } = useAuth();
  const toast = useToast();

  const getBreadcrumbs = () => {
    const parts = location.pathname.split('/').filter(Boolean);
    if (parts.length === 0) return 'Dashboard';

    const cleanName = parts[parts.length - 1]
      .replace(/-/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());

    return cleanName;
  };

  const handleQuickSwitch = async (role) => {
    try {
      if (role === 'teacher') {
        await login('teacher@evalagent.com', 'password123');
        toast.info('Switched to Teacher account (Dr. Alexander Wright)');
        navigate('/teacher/dashboard');
      } else {
        await login('student1@evalagent.com', 'password123');
        toast.info('Switched to Student account (Rahul Sharma)');
        navigate('/student/dashboard');
      }
    } catch (err) {
      toast.error('Could not switch demo user. Please make sure the database is seeded.');
    }
  };

  return (
    <header className="topbar">
      {/* Breadcrumb path */}
      <div className="topbar-breadcrumbs">
        <span>AutoEval</span>
        <ChevronRight size={14} />
        <span className="current">{getBreadcrumbs()}</span>
      </div>

      {/* Actions & Status */}
      <div className="topbar-actions">
        {/* System Engine indicator */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            background: '#ecfdf5',
            border: '1px solid #a7f3d0',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: '#065f46',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: 'var(--success)',
              boxShadow: '0 0 6px var(--success)',
            }}
          />
          Multi-Agent RAG Engine Active
        </div>

        {/* Demo Fast Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Quick Role:</span>
          <button
            onClick={() => handleQuickSwitch(user?.role === 'teacher' ? 'student' : 'teacher')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '5px 10px',
              borderRadius: 'var(--radius-md)',
              background: '#ffffff',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-primary)',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: 'var(--shadow-xs)',
              transition: 'all var(--transition-fast)',
            }}
            title="Switch between Teacher and Student Demo accounts in 1-click"
          >
            <Sparkles size={13} color="var(--primary-500)" />
            Switch to {user?.role === 'teacher' ? 'Student View' : 'Teacher View'}
          </button>
        </div>
      </div>
    </header>
  );
};
