import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, GraduationCap, School } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';

export const RegisterPage = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('student');
  const [studentId, setStudentId] = useState('');
  const [department, setDepartment] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fullName || !email || !password) {
      toast.error('Please fill in all required fields.');
      return;
    }

    setIsLoading(true);
    try {
      const user = await register({
        full_name: fullName,
        email,
        password,
        role,
        student_id: role === 'student' ? studentId : null,
        department,
      });

      toast.success(`Account created! Welcome, ${user.full_name}.`);
      if (user.role === 'teacher' || user.role === 'admin') {
        navigate('/teacher/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(msg);
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
          maxWidth: '480px',
          padding: '2.5rem',
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          boxShadow: 'var(--shadow-xl)',
          borderRadius: 'var(--radius-lg)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
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
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)' }}>Create an Account</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Join the automated evaluation portal
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Role selector */}
          <div className="form-group">
            <label className="form-label">I am joining as a:</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <button
                type="button"
                className={`btn ${role === 'student' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setRole('student')}
                style={{ justifyContent: 'center' }}
              >
                <GraduationCap size={16} />
                Student
              </button>
              <button
                type="button"
                className={`btn ${role === 'teacher' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setRole('teacher')}
                style={{ justifyContent: 'center' }}
              >
                <School size={16} />
                Instructor
              </button>
            </div>
          </div>

          <Input
            label="Full Name"
            placeholder="e.g. Rahul Sharma"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />

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
            placeholder="Minimum 6 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {role === 'student' && (
            <Input
              label="Student ID Number"
              placeholder="e.g. CS2025-01"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
            />
          )}

          <Input
            label="Department / Course"
            placeholder="e.g. Computer Science"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
          />

          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            style={{ width: '100%', marginTop: '0.75rem' }}
          >
            Create Account
          </Button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ fontWeight: 600, color: 'var(--primary-500)' }}>
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
};
