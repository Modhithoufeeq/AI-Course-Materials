import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, BookOpen, Calendar, Users, FileText, ArrowRight, Trash2 } from 'lucide-react';
import { assignmentService } from '../../services/assignmentService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { formatDate } from '../../utils/formatters';
import { getStatusBadge } from '../../utils/statusBadges';

export const AssignmentsPage = () => {
  const [assignments, setAssignments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const toast = useToast();

  const fetchAssignments = async () => {
    try {
      const data = await assignmentService.listAssignments();
      setAssignments(data);
    } catch (err) {
      toast.error('Failed to load assignments.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignments();
  }, []);

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete '${title}'? All submissions and rubrics will be removed.`)) {
      return;
    }
    try {
      await assignmentService.deleteAssignment(id);
      toast.success(`Assignment '${title}' deleted.`);
      fetchAssignments();
    } catch (err) {
      toast.error('Failed to delete assignment.');
    }
  };

  if (isLoading) {
    return <Loader message="Loading course assignments..." size="lg" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
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
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Course Assignments</h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Manage assignment briefs, rubric criteria, reference documents, and submissions.
          </p>
        </div>

        <Link to="/teacher/assignments/create">
          <Button variant="primary" icon={PlusCircle}>
            Create New Assignment
          </Button>
        </Link>
      </div>

      {assignments.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
          <BookOpen size={48} color="var(--primary-500)" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>No assignments created yet</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.35rem', marginBottom: '1.5rem' }}>
            Get started by creating your first automated evaluation assignment with a rubric.
          </p>
          <Link to="/teacher/assignments/create">
            <Button variant="primary" icon={PlusCircle}>
              Create Assignment
            </Button>
          </Link>
        </Card>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.5rem' }}>
          {assignments.map((a) => {
            const statusBadge = getStatusBadge(a.status);
            return (
              <Card
                key={a.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  height: '100%',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    {a.code && (
                      <span
                        style={{
                          fontSize: '0.75rem',
                          fontFamily: 'var(--font-mono)',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '4px',
                          background: 'rgba(79, 70, 229, 0.08)',
                          color: 'var(--primary-500)',
                        }}
                      >
                        {a.code}
                      </span>
                    )}
                    <span className={`badge ${statusBadge.className}`}>{statusBadge.label}</span>
                  </div>

                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.4rem', color: 'var(--text-primary)' }}>{a.title}</h3>
                  <p
                    style={{
                      fontSize: '0.85rem',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.5,
                      marginBottom: '1.25rem',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                  >
                    {a.description || a.instructions}
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Calendar size={14} />
                      <span>Due: {formatDate(a.due_date)}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <FileText size={14} />
                      <span>
                        Submissions: <strong style={{ color: 'var(--text-primary)' }}>{a.submission_count || 0}</strong> ({a.evaluated_count || 0} evaluated)
                      </span>
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    paddingTop: '1rem',
                    borderTop: '1px solid var(--border-subtle)',
                  }}
                >
                  <button
                    onClick={() => handleDelete(a.id, a.title)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      padding: '6px',
                      borderRadius: 'var(--radius-sm)',
                    }}
                    title="Delete Assignment"
                  >
                    <Trash2 size={16} />
                  </button>

                  <Link to={`/teacher/assignments/${a.id}`}>
                    <Button variant="secondary" size="sm" icon={ArrowRight}>
                      View Submissions
                    </Button>
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
