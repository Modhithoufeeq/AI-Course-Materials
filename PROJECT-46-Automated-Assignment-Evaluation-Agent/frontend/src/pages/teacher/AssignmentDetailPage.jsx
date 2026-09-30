import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Calendar,
  Sliders,
  FileText,
  UploadCloud,
  Sparkles,
  Award,
  ArrowLeft,
  CheckCircle2,
  Users,
} from 'lucide-react';
import { assignmentService } from '../../services/assignmentService';
import { submissionService } from '../../services/submissionService';
import { evaluationService } from '../../services/evaluationService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { formatDate } from '../../utils/formatters';
import { getStatusBadge } from '../../utils/statusBadges';

export const AssignmentDetailPage = () => {
  const { id } = useParams();
  const [assignment, setAssignment] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [evaluatingSubId, setEvaluatingSubId] = useState(null);

  const toast = useToast();
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const [assignData, subsData] = await Promise.all([
        assignmentService.getAssignment(id),
        submissionService.listSubmissions({ assignmentId: id }),
      ]);
      setAssignment(assignData);
      setSubmissions(subsData);
    } catch (err) {
      toast.error('Failed to load assignment details.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleStartEvaluation = async (submissionId) => {
    setEvaluatingSubId(submissionId);
    try {
      toast.info('Starting Multi-Agent AI evaluation pipeline...');
      await evaluationService.startEvaluation(submissionId);
      toast.success('Evaluation complete! Result is now under review.');
      await loadData();
      navigate(`/teacher/evaluations/${submissionId}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Evaluation failed.');
    } finally {
      setEvaluatingSubId(null);
    }
  };

  if (isLoading) {
    return <Loader message="Loading assignment and student submissions..." size="lg" />;
  }

  if (!assignment) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <h3>Assignment not found</h3>
        <Link to="/teacher/assignments">
          <Button variant="secondary" icon={ArrowLeft} style={{ marginTop: '1rem' }}>
            Back to Assignments
          </Button>
        </Link>
      </div>
    );
  }

  const rubric = assignment.rubrics?.[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Header */}
      <div>
        <Link to="/teacher/assignments" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
          <ArrowLeft size={14} /> Back to Assignments
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>{assignment.title}</h1>
              {assignment.code && (
                <span style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', fontWeight: 700, padding: '2px 8px', borderRadius: '4px', background: 'rgba(79, 70, 229, 0.08)', color: 'var(--primary-500)' }}>
                  {assignment.code}
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Due: {formatDate(assignment.due_date)} • Max Score: {assignment.max_score} pts
            </p>
          </div>
        </div>
      </div>

      {/* Grid: Instructions & Rubric summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '1.5rem' }}>
        {/* Instructions */}
        <Card title="Assignment Instructions">
          <div
            style={{
              fontSize: '0.9rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
              maxHeight: '260px',
              overflowY: 'auto',
              paddingRight: '0.5rem',
            }}
          >
            {assignment.instructions}
          </div>
        </Card>

        {/* Rubric Criteria */}
        <Card
          title={rubric?.title || 'Evaluation Rubric'}
          subtitle={`Total: ${rubric?.total_points || 100} points`}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {rubric?.criteria?.map((c) => (
              <div
                key={c.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: '#f8fafc',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{c.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{c.description}</div>
                </div>
                <span style={{ fontWeight: 700, color: 'var(--primary-500)', fontSize: '0.9rem' }}>
                  {c.max_points} pts
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Submissions Table for this Assignment */}
      <Card
        title={`Student Submissions (${submissions.length})`}
        subtitle="Manage and evaluate student files for this assignment"
      >
        {submissions.length === 0 ? (
          <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No submissions uploaded yet for this assignment.
          </p>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>File Details</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Similarity</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((sub) => {
                  const statusBadge = getStatusBadge(sub.status);
                  return (
                    <tr key={sub.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{sub.student?.full_name || `Student #${sub.student_id}`}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sub.student?.email}</div>
                      </td>
                      <td>
                        <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <FileText size={14} color="var(--primary-500)" />
                          {sub.file_name}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {sub.word_count} words • {formatDate(sub.submitted_at)}
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${statusBadge.className}`}>{statusBadge.label}</span>
                      </td>
                      <td>
                        {sub.total_score !== null && sub.total_score !== undefined ? (
                          <strong style={{ color: 'var(--text-primary)' }}>
                            {sub.total_score} / {sub.max_possible_score || 100}
                          </strong>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>
                      <td>
                        {sub.similarity_percentage !== null && sub.similarity_percentage !== undefined ? (
                          <span style={{ fontWeight: 600, color: sub.similarity_percentage > 40 ? 'var(--danger)' : 'var(--success)' }}>
                            {sub.similarity_percentage}%
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          {sub.status === 'extracted' || sub.status === 'pending' ? (
                            <Button
                              size="sm"
                              variant="primary"
                              icon={Sparkles}
                              onClick={() => handleStartEvaluation(sub.id)}
                              isLoading={evaluatingSubId === sub.id}
                            >
                              Evaluate
                            </Button>
                          ) : (
                            <Link to={`/teacher/evaluations/${sub.id}`}>
                              <Button size="sm" variant="secondary">
                                Review & Publish
                              </Button>
                            </Link>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
