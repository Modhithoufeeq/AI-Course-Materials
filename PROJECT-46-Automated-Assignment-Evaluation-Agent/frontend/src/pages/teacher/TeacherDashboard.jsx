import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Users,
  Clock,
  CheckCircle2,
  Award,
  TrendingUp,
  PlusCircle,
  UploadCloud,
  ArrowRight,
  Sparkles,
  AlertCircle,
} from 'lucide-react';
import { dashboardService } from '../../services/dashboardService';
import { evaluationService } from '../../services/evaluationService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { getStatusBadge } from '../../utils/statusBadges';

export const TeacherDashboard = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [evaluatingSubId, setEvaluatingSubId] = useState(null);
  const toast = useToast();
  const navigate = useNavigate();

  const fetchDashboardData = async () => {
    try {
      const data = await dashboardService.getTeacherDashboard();
      setStats(data);
    } catch (err) {
      toast.error('Failed to load dashboard metrics.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleStartEvaluation = async (submissionId) => {
    setEvaluatingSubId(submissionId);
    try {
      toast.info('Starting Multi-Agent AI evaluation pipeline...');
      const evalResult = await evaluationService.startEvaluation(submissionId);
      toast.success('AI Evaluation complete! Result is now under review.');
      await fetchDashboardData();
      navigate(`/teacher/evaluations/${submissionId}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Evaluation failed.');
    } finally {
      setEvaluatingSubId(null);
    }
  };

  if (isLoading) {
    return <Loader message="Aggregating course analytics & evaluation queues..." size="lg" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header Banner with Quick Actions */}
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
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Instructor Dashboard</h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Monitor automated rubric grading, similarity indicators, and review queues.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Link to="/teacher/submissions">
            <Button variant="secondary" icon={UploadCloud}>
              Submissions Pool
            </Button>
          </Link>
          <Link to="/teacher/assignments/create">
            <Button variant="primary" icon={PlusCircle}>
              Create Assignment
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ color: 'var(--primary-500)', background: '#eef2ff' }}>
            <BookOpen size={24} />
          </div>
          <div>
            <div className="stat-label">Active Assignments</div>
            <div className="stat-value">{stats?.total_assignments || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ color: '#0284c7', background: '#f0f9ff' }}>
            <Users size={24} />
          </div>
          <div>
            <div className="stat-label">Enrolled Students</div>
            <div className="stat-value">{stats?.total_students || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ color: 'var(--warning)', background: '#fffbeb' }}>
            <Clock size={24} />
          </div>
          <div>
            <div className="stat-label">Under Review</div>
            <div className="stat-value">{stats?.under_review_evaluations || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ color: 'var(--success)', background: '#ecfdf5' }}>
            <Award size={24} />
          </div>
          <div>
            <div className="stat-label">Published Grades</div>
            <div className="stat-value">{stats?.published_results || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ color: 'var(--purple)', background: '#f5f3ff' }}>
            <TrendingUp size={24} />
          </div>
          <div>
            <div className="stat-label">Average Score</div>
            <div className="stat-value">{stats?.average_score_percentage || 0}%</div>
          </div>
        </div>
      </div>

      {/* Main Content Grid: Recent Submissions + Grade Distribution */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.5rem' }}>
        {/* Recent Submissions Queue */}
        <Card
          title="Recent Submission Queue"
          subtitle="Real-time student uploads awaiting evaluation or review"
          action={
            <Link to="/teacher/submissions" style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              View All <ArrowRight size={14} />
            </Link>
          }
        >
          {stats?.recent_submissions?.length === 0 ? (
            <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
              No submissions uploaded yet. Create an assignment to begin!
            </p>
          ) : (
            <div className="table-container" style={{ border: 'none' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Assignment</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {stats?.recent_submissions?.map((sub) => {
                    const badge = getStatusBadge(sub.status);
                    return (
                      <tr key={sub.id}>
                        <td>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{sub.student_name}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sub.timestamp}</div>
                        </td>
                        <td style={{ color: 'var(--text-secondary)' }}>{sub.assignment_title}</td>
                        <td>
                          <span className={`badge ${badge.className}`}>{badge.label}</span>
                        </td>
                        <td>
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
                                Review
                              </Button>
                            </Link>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Grade Distribution Breakdown */}
        <Card title="Grade Distribution" subtitle="Cohort performance across published letter grades">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
            {stats?.grade_distribution?.map((g, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{g.grade_range}</span>
                  <span style={{ color: 'var(--text-muted)' }}>
                    {g.count} students ({g.percentage}%)
                  </span>
                </div>
                <div className="progress-bar-container">
                  <div
                    className="progress-bar-fill"
                    style={{
                      width: `${Math.max(2, g.percentage)}%`,
                      background: idx === 0 ? 'var(--success)' : idx === 1 ? '#0284c7' : idx === 2 ? 'var(--warning)' : 'var(--danger)',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
