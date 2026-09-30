import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  UploadCloud,
  CheckCircle2,
  Users,
  Award,
  LogOut,
  Sparkles,
  Layers,
  BookOpen,
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const Sidebar = () => {
  const { user, isTeacher, isStudent, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">
          <Sparkles size={20} />
        </div>
        <span className="sidebar-brand-title">AutoEval AI</span>
        <span className="sidebar-role-badge">
          {user?.role || 'Guest'}
        </span>
      </div>

      {/* Nav Links */}
      <nav className="sidebar-nav">
        {isTeacher && (
          <>
            <span className="sidebar-nav-heading">Overview</span>
            <NavLink to="/teacher/dashboard" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <LayoutDashboard />
              <span>Dashboard</span>
            </NavLink>

            <span className="sidebar-nav-heading">Course Management</span>
            <NavLink to="/teacher/assignments" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <FileText />
              <span>Assignments</span>
            </NavLink>
            <NavLink to="/teacher/assignments/create" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <PlusCircle />
              <span>Create Assignment</span>
            </NavLink>
            <NavLink to="/teacher/students" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Users />
              <span>Student Roster</span>
            </NavLink>

            <span className="sidebar-nav-heading">Evaluation Pipeline</span>
            <NavLink to="/teacher/submissions" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <UploadCloud />
              <span>Submissions</span>
            </NavLink>
            <NavLink to="/teacher/published-results" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Award />
              <span>Published Grades</span>
            </NavLink>
          </>
        )}

        {isStudent && (
          <>
            <span className="sidebar-nav-heading">Student Portal</span>
            <NavLink to="/student/dashboard" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <LayoutDashboard />
              <span>My Dashboard</span>
            </NavLink>
            <NavLink to="/student/assignments" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <BookOpen />
              <span>My Assignments</span>
            </NavLink>
            <NavLink to="/student/results" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Award />
              <span>Graded Results</span>
            </NavLink>
          </>
        )}
      </nav>

      {/* User Footer Profile */}
      <div className="sidebar-footer">
        <div className="user-profile-pill">
          <div className="user-avatar">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div className="user-info">
            <div className="user-name">{user?.full_name || 'User Account'}</div>
            <div className="user-role-label">{user?.email}</div>
          </div>
          <button
            onClick={handleLogout}
            title="Logout"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
              transition: 'color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--danger)')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};
