import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Award,
  UploadCloud,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
  FileText,
} from 'lucide-react';
import { dashboardService } from '../../services/dashboardService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { formatDate, formatPercentage } from '../../utils/formatters';
import { getGradeColor } from '../../utils/statusBadges';

export const StudentDashboard = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await dashboardService.getStudentDashboard();
        setStats(data);
      } catch (err) {
        toast.error('Failed to load student dashboard.');
      } finally {
        setIsLoading(false);
      }
    };
    loadStats();
  }, []);

  if (isLoading) {
    return <Loader message="Loading your student profile and grades..." size="lg" />;
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
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Student Portal</h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Submit assignment solutions and view detailed AI evaluation reports with rubric feedback.
          </p>
        </div>

        <Link to="/student/assignments">
          <Button variant="primary" icon={UploadCloud}>
            Submit Assignment
          </Button>
        </Link>
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
            <UploadCloud size={24} />
          </div>
          <div>
            <div className="stat-label">Submitted</div>
            <div className="stat-value">{stats?.my_submissions || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ color: 'var(--success)', background: '#ecfdf5' }}>
            <Award size={24} />
          </div>
          <div>
            <div className="stat-label">Graded Results</div>
            <div className="stat-value">{stats?.my_graded_results || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ color: 'var(--purple)', background: '#f5f3ff' }}>
            <TrendingUp size={24} />
          </div>
          <div>
            <div className="stat-label">Overall Average</div>
            <div className="stat-value">{stats?.average_percentage || 0}%</div>
          </div>
        </div>
      </div>

      {/* Recent Published Results */}
      <Card
        title="Recently Published Grades"
        subtitle="Official instructor-approved scores and personalized feedback reports"
        action={
          <Link to="/student/results" style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            All Grades <ArrowRight size={14} />
          </Link>
        }
      >
        {stats?.recent_grades?.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
            <Award size={36} color="var(--primary-500)" style={{ margin: '0 auto 0.5rem' }} />
            <p>No graded results published yet. Submit an assignment to get evaluated!</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {stats?.recent_grades?.map((res) => (
              <div
                key={res.id}
                style={{
                  padding: '1.25rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: '#ffffff',
                  border: '1px solid var(--border-subtle)',
                  boxShadow: 'var(--shadow-xs)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Published {formatDate(res.published_at)}
                    </span>
                    <span
                      style={{
                        fontSize: '1.2rem',
                        fontWeight: 800,
                        color: getGradeColor(res.letter_grade),
                      }}
                    >
                      {res.letter_grade}
                    </span>
                  </div>

                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                    {res.assignment_title}
                  </h4>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                    <div>
                      <span style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                        {res.final_score}
                      </span>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}> / {res.max_score} pts</span>
                    </div>
                    <span className="badge badge-success">{formatPercentage(res.percentage)}</span>
                  </div>
                </div>

                <Link to={`/student/results/${res.id}`}>
                  <Button variant="secondary" size="sm" icon={ArrowRight} style={{ width: '100%' }}>
                    View Full Evaluation Report
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
