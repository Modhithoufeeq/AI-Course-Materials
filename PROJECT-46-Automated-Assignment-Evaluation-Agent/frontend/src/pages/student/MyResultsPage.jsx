import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Award, ArrowRight, FileText, CheckCircle2, TrendingUp } from 'lucide-react';
import { resultService } from '../../services/resultService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { formatDate, formatPercentage } from '../../utils/formatters';
import { getGradeColor } from '../../utils/statusBadges';

export const MyResultsPage = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const loadResults = async () => {
      try {
        const data = await resultService.listResults();
        setResults(data);
      } catch (err) {
        toast.error('Failed to load graded results.');
      } finally {
        setIsLoading(false);
      }
    };
    loadResults();
  }, []);

  if (isLoading) {
    return <Loader message="Loading your graded assignment reports..." size="lg" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>My Graded Results</h1>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
          Official scores, criteria evaluations, and actionable feedback approved by your instructors.
        </p>
      </div>

      {results.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: '3.5rem 1.5rem' }}>
          <Award size={48} color="var(--primary-500)" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>No graded results published yet</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.35rem', marginBottom: '1.5rem' }}>
            When your instructors review and release evaluations, your detailed grade report will appear here.
          </p>
          <Link to="/student/assignments">
            <Button variant="primary">
              View Active Assignments
            </Button>
          </Link>
        </Card>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem' }}>
          {results.map((res) => (
            <Card
              key={res.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: '100%',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Published {formatDate(res.published_at)}
                  </span>
                  <span
                    style={{
                      fontSize: '1.35rem',
                      fontWeight: 800,
                      color: getGradeColor(res.letter_grade),
                    }}
                  >
                    {res.letter_grade || '—'}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
                  {res.assignment_title}
                </h3>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem' }}>
                  <div>
                    <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {res.final_score}
                    </span>
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}> / {res.max_score} pts</span>
                  </div>
                  <span className="badge badge-success" style={{ fontSize: '0.85rem' }}>
                    {formatPercentage(res.percentage)}
                  </span>
                </div>

                {res.summary && (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '1rem', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {res.summary}
                  </p>
                )}
              </div>

              <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
                <Link to={`/student/results/${res.id}`}>
                  <Button variant="secondary" icon={ArrowRight} style={{ width: '100%' }}>
                    View Full Detailed Report
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
