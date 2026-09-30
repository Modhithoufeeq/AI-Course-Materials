import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import confetti from 'canvas-confetti';
import {
  Sparkles,
  Award,
  FileText,
  Sliders,
  ShieldCheck,
  Cpu,
  RefreshCw,
  Edit3,
  CheckCircle2,
  ArrowLeft,
  BookOpen,
} from 'lucide-react';
import { evaluationService } from '../../services/evaluationService';
import { submissionService } from '../../services/submissionService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { CriterionScorer } from '../../components/evaluation/CriterionScorer';
import { OriginalityMeter } from '../../components/evaluation/OriginalityMeter';
import { FeedbackEditor } from '../../components/evaluation/FeedbackEditor';
import { AgentLogViewer } from '../../components/evaluation/AgentLogViewer';
import { TeacherReviewModal } from '../../components/evaluation/TeacherReviewModal';
import { formatDate, formatPercentage } from '../../utils/formatters';
import { getStatusBadge, getGradeColor } from '../../utils/statusBadges';

export const EvaluationDetailPage = () => {
  const { submissionId } = useParams();
  const [evaluation, setEvaluation] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [activeTab, setActiveTab] = useState('rubric'); // rubric, originality, feedback, logs
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isReevaluating, setIsReevaluating] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const [evalData, subData] = await Promise.all([
        evaluationService.getEvaluation(submissionId),
        submissionService.getSubmission(submissionId),
      ]);
      setEvaluation(evalData);
      setSubmission(subData);
    } catch (err) {
      toast.error('Failed to load evaluation details.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [submissionId]);

  const handleReevaluate = async () => {
    setIsReevaluating(true);
    try {
      toast.info('Re-running multi-agent evaluation pipeline...');
      const fresh = await evaluationService.reevaluate(submissionId);
      setEvaluation(fresh);
      toast.success('Re-evaluation completed successfully!');
    } catch (err) {
      toast.error('Re-evaluation failed.');
    } finally {
      setIsReevaluating(false);
    }
  };

  const handleQuickPublish = async () => {
    setIsPublishing(true);
    try {
      await evaluationService.approveEvaluation(evaluation.id, {
        publish_immediately: true,
      });
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
      });
      toast.success('Grade approved and published to student!');
      await loadData();
    } catch (err) {
      toast.error('Failed to publish evaluation.');
    } finally {
      setIsPublishing(false);
    }
  };

  if (isLoading) {
    return <Loader message="Loading evaluation analysis, vector matches, and agent logs..." size="lg" />;
  }

  if (!evaluation || !submission) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <h3>No evaluation found for this submission</h3>
        <Link to="/teacher/submissions">
          <Button variant="secondary" icon={ArrowLeft} style={{ marginTop: '1rem' }}>
            Back to Submissions
          </Button>
        </Link>
      </div>
    );
  }

  const statusBadge = getStatusBadge(evaluation.status);
  const isPublished = evaluation.status === 'published' || !!evaluation.published_result;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header Bar */}
      <div>
        <Link to="/teacher/submissions" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
          <ArrowLeft size={14} /> Back to Submissions
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Evaluation & Review</h1>
              <span className={`badge ${statusBadge.className}`}>{statusBadge.label}</span>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Student: <strong style={{ color: 'var(--text-primary)' }}>{submission.student?.full_name}</strong> ({submission.student?.email}) • File: {submission.file_name}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <Button
              variant="secondary"
              icon={RefreshCw}
              onClick={handleReevaluate}
              isLoading={isReevaluating}
            >
              Re-run AI Agents
            </Button>
            <Button
              variant="primary"
              icon={Edit3}
              onClick={() => setIsReviewModalOpen(true)}
            >
              Review / Modify Scores
            </Button>
            {!isPublished && (
              <Button
                variant="success"
                icon={Award}
                onClick={handleQuickPublish}
                isLoading={isPublishing}
              >
                Publish Grade
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Top Banner Metric Summary */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.25rem',
          padding: '1.25rem 1.5rem',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div>
          <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Calculated Score
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            {evaluation.total_score} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ {evaluation.max_possible_score}</span>
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Percentage
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--primary-500)' }}>
            {formatPercentage(evaluation.percentage)}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Letter Grade
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: getGradeColor(evaluation.letter_grade) }}>
            {evaluation.letter_grade || '—'}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Originality Index
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: evaluation.originality_report?.similarity_percentage > 40 ? 'var(--danger)' : 'var(--success)' }}>
            {evaluation.originality_report?.similarity_percentage ?? 0}%
          </div>
        </div>
      </div>

      {/* Main 2-Column Split: Document Viewer (Left) & Evaluation Tabs (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 42%) 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Left: Extracted Document Content */}
        <Card title="Submitted Document Content" subtitle={`${submission.file_name} • ${submission.word_count || 0} words`}>
          <div
            style={{
              padding: '1.25rem',
              borderRadius: 'var(--radius-md)',
              backgroundColor: '#f8fafc',
              border: '1px solid var(--border-subtle)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.825rem',
              lineHeight: 1.6,
              color: '#334155',
              maxHeight: '650px',
              overflowY: 'auto',
              whiteSpace: 'pre-wrap',
            }}
          >
            {submission.extracted_text || 'No text extracted.'}
          </div>
        </Card>

        {/* Right: Tabbed Evaluation Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Tabs Navigation */}
          <div
            style={{
              display: 'flex',
              gap: '0.5rem',
              borderBottom: '1px solid var(--border-subtle)',
              paddingBottom: '0.5rem',
              flexWrap: 'wrap',
            }}
          >
            <button
              onClick={() => setActiveTab('rubric')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '8px 16px',
                borderRadius: 'var(--radius-md)',
                background: activeTab === 'rubric' ? 'var(--primary-gradient)' : '#ffffff',
                border: '1px solid',
                borderColor: activeTab === 'rubric' ? 'transparent' : 'var(--border-subtle)',
                color: activeTab === 'rubric' ? 'white' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                boxShadow: activeTab === 'rubric' ? 'var(--shadow-sm)' : 'none',
              }}
            >
              <Sliders size={16} /> Rubric Breakdown
            </button>

            <button
              onClick={() => setActiveTab('originality')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '8px 16px',
                borderRadius: 'var(--radius-md)',
                background: activeTab === 'originality' ? 'var(--primary-gradient)' : '#ffffff',
                border: '1px solid',
                borderColor: activeTab === 'originality' ? 'transparent' : 'var(--border-subtle)',
                color: activeTab === 'originality' ? 'white' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                boxShadow: activeTab === 'originality' ? 'var(--shadow-sm)' : 'none',
              }}
            >
              <ShieldCheck size={16} /> Originality Check
            </button>

            <button
              onClick={() => setActiveTab('feedback')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '8px 16px',
                borderRadius: 'var(--radius-md)',
                background: activeTab === 'feedback' ? 'var(--primary-gradient)' : '#ffffff',
                border: '1px solid',
                borderColor: activeTab === 'feedback' ? 'transparent' : 'var(--border-subtle)',
                color: activeTab === 'feedback' ? 'white' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                boxShadow: activeTab === 'feedback' ? 'var(--shadow-sm)' : 'none',
              }}
            >
              <Sparkles size={16} /> Feedback & Action Items
            </button>

            <button
              onClick={() => setActiveTab('logs')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '8px 16px',
                borderRadius: 'var(--radius-md)',
                background: activeTab === 'logs' ? 'var(--primary-gradient)' : '#ffffff',
                border: '1px solid',
                borderColor: activeTab === 'logs' ? 'transparent' : 'var(--border-subtle)',
                color: activeTab === 'logs' ? 'white' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                boxShadow: activeTab === 'logs' ? 'var(--shadow-sm)' : 'none',
              }}
            >
              <Cpu size={16} /> Agent Logs
            </button>
          </div>

          {/* Tab Views */}
          {activeTab === 'rubric' && (
            <CriterionScorer
              criterionScores={evaluation.criterion_scores}
              isEditable={false}
            />
          )}

          {activeTab === 'originality' && (
            <OriginalityMeter originalityReport={evaluation.originality_report} />
          )}

          {activeTab === 'feedback' && (
            <FeedbackEditor
              feedback={evaluation.feedback}
              teacherCustomFeedback={evaluation.feedback?.teacher_custom_feedback || evaluation.teacher_notes}
              isEditable={false}
            />
          )}

          {activeTab === 'logs' && (
            <Card>
              <AgentLogViewer logs={evaluation.decision_logs} />
            </Card>
          )}
        </div>
      </div>

      {/* Teacher Review & Score Editor Modal */}
      <TeacherReviewModal
        isOpen={isReviewModalOpen}
        onClose={() => setIsReviewModalOpen(false)}
        evaluation={evaluation}
        onEvaluationUpdated={(updated) => {
          setEvaluation(updated);
          loadData();
        }}
      />
    </div>
  );
};
