import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Award, ArrowLeft, Printer, CheckCircle2, FileText, UserCheck } from 'lucide-react';
import { resultService } from '../../services/resultService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { CriterionScorer } from '../../components/evaluation/CriterionScorer';
import { FeedbackEditor } from '../../components/evaluation/FeedbackEditor';
import { formatDate, formatPercentage } from '../../utils/formatters';
import { getGradeColor } from '../../utils/statusBadges';

export const StudentResultDetailPage = () => {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const loadResult = async () => {
      try {
        const data = await resultService.getResultDetail(id);
        setResult(data);
      } catch (err) {
        toast.error('Failed to load graded report.');
      } finally {
        setIsLoading(false);
      }
    };
    loadResult();
  }, [id]);

  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return <Loader message="Generating your official evaluation report..." size="lg" />;
  }

  if (!result) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <h3>Graded report not found</h3>
        <Link to="/student/results">
          <Button variant="secondary" icon={ArrowLeft} style={{ marginTop: '1rem' }}>
            Back to My Results
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '880px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <Link to="/student/results" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
          <ArrowLeft size={14} /> Back to My Results
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>{result.assignment_title}</h1>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Reviewed & Released by {result.teacher?.full_name || 'Course Instructor'} • {formatDate(result.published_at)}
            </p>
          </div>

          <Button variant="secondary" icon={Printer} onClick={handlePrint}>
            Print Report
          </Button>
        </div>
      </div>

      {/* Grade Hero Banner */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.5rem',
          padding: '1.75rem 2rem',
          borderRadius: 'var(--radius-lg)',
          background: 'linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%)',
          border: '1px solid #e2e8f0',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Final Grade
          </div>
          <div
            style={{
              fontSize: '3rem',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              lineHeight: 1.1,
              marginTop: '0.2rem',
              color: getGradeColor(result.letter_grade),
            }}
          >
            {result.letter_grade || '—'}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Total Awarded Score
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.2, marginTop: '0.2rem' }}>
            {result.final_score}{' '}
            <span style={{ fontSize: '1.15rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              / {result.max_score} pts
            </span>
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Percentage
          </div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary-500)', lineHeight: 1.2, marginTop: '0.2rem' }}>
            {formatPercentage(result.percentage)}
          </div>
        </div>
      </div>

      {/* Rubric Breakdown */}
      <Card title="Rubric Criteria Assessment" subtitle="Detailed point allocation, evaluation rationale, and extracted text evidence">
        <CriterionScorer
          criterionScores={result.criterion_scores || []}
          isEditable={false}
        />
      </Card>

      {/* Qualitative Feedback */}
      {result.feedback && (
        <Card title="Comprehensive Feedback & Recommendations">
          <FeedbackEditor
            feedback={result.feedback}
            teacherCustomFeedback={result.feedback.teacher_custom_feedback}
            isEditable={false}
          />
        </Card>
      )}
    </div>
  );
};
