import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Mail, BookOpen, GraduationCap } from 'lucide-react';
import { studentService } from '../../services/studentService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Loader } from '../../components/common/Loader';
import { formatDate } from '../../utils/formatters';

export const StudentsPage = () => {
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [studentId, setStudentId] = useState('');
  const [department, setDepartment] = useState('');

  const toast = useToast();

  const loadStudents = async () => {
    try {
      const data = await studentService.listStudents();
      setStudents(data);
    } catch (err) {
      toast.error('Failed to load students roster.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, []);

  const handleAddStudent = async (e) => {
    e.preventDefault();
    if (!fullName || !email) {
      toast.error('Name and email are required.');
      return;
    }

    setIsSubmitting(true);
    try {
      await studentService.createStudent({
        full_name: fullName,
        email,
        student_id: studentId,
        department,
        password: 'password123',
      });
      toast.success(`Enrolled student ${fullName}. (Default password: password123)`);
      setIsAddModalOpen(false);
      setFullName('');
      setEmail('');
      setStudentId('');
      setDepartment('');
      await loadStudents();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to enroll student.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <Loader message="Loading enrolled student roster..." size="lg" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          paddingBottom: '1rem',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Student Roster</h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Manage course enrollments, student identifiers, and department assignments.
          </p>
        </div>

        <Button variant="primary" icon={UserPlus} onClick={() => setIsAddModalOpen(true)}>
          Enroll New Student
        </Button>
      </div>

      {/* Roster Table */}
      <Card title={`Enrolled Students (${students.length})`}>
        <div className="table-container" style={{ border: 'none' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Student ID</th>
                <th>Department</th>
                <th>Enrolled Date</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr key={s.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div
                        style={{
                          width: '34px',
                          height: '34px',
                          borderRadius: '50%',
                          background: 'var(--secondary-gradient)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          color: 'white',
                          fontSize: '0.85rem',
                        }}
                      >
                        {s.full_name?.charAt(0)}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{s.full_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.email}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {s.student_id || '—'}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{s.department || 'Computer Science'}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{formatDate(s.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Enroll Student Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Enroll New Student"
        footer={
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Button variant="secondary" onClick={() => setIsAddModalOpen(false)} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button variant="primary" icon={UserPlus} onClick={handleAddStudent} isLoading={isSubmitting}>
              Enroll Student
            </Button>
          </div>
        }
      >
        <form onSubmit={handleAddStudent}>
          <Input
            label="Full Name *"
            placeholder="e.g. Maria Gonzalez"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />

          <Input
            label="Email Address *"
            type="email"
            placeholder="mgonzalez@institution.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <Input
            label="Student ID"
            placeholder="e.g. CS2025-06"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
          />

          <Input
            label="Department"
            placeholder="e.g. Computer Science & AI"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
          />
        </form>
      </Modal>
    </div>
  );
};
