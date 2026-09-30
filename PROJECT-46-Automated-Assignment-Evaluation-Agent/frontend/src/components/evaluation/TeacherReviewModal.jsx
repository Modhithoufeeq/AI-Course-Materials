import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { CriterionScorer } from './CriterionScorer';
import { evaluationService } from '../../services/evaluationService';
import { useToast } from '../../hooks/useToast';
import { CheckCircle2, Award, Save, Sparkles } from 'lucide-react';
import { formatPercentage } from '../../utils/formatters';

export const TeacherReviewModal = ({
  isOpen,
  onClose,
  evaluation,
  onEvaluationUpdated,
}) => {
  const [scores, setScores] = useState([]);
  const [teacherNotes, setTeacherNotes] = useState('');
  const [teacherFeedback, setTeacherFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (evaluation) {
      setScores(
        (evaluation.criterion_scores || []).map((c) => ({
          criterion_id: c.criterion_id,
          criterion_name: c.criterion_name,
          max_points: c.max_points,
          score: c.teacher_modified_score !== null && c.teacher_modified_score !== undefined ? c.teacher_modified_score : c.score,
          rationale: c.rationale,
          evidence_quote: c.evidence_quote,
        }))
      );
      setTeacherNotes(evaluation.teacher_notes || '');
      setTeacherFeedback(evaluation.feedback?.teacher_custom_feedback || '');
    }
  }, [evaluation]);

  if (!evaluation) return null;

  const handleScoreChange = (criterionId, newScore) => {
    setScores((prev) =>
      prev.map((c) => {
        if (c.criterion_id === criterionId) {
          const bounded = Math.max(0, Math.min(newScore, c.max_points));
          return { ...c, score: bounded };
        }
        return c;
      })
    );
  };

  // Programmatic live calculation of total score
  const computedTotal = scores.reduce((sum, c) => sum + (parseFloat(c.score) || 0), 0);
  const maxPossible = evaluation.max_possible_score || 100;
  const computedPct = (computedTotal / maxPossible) * 100;

  const handleSave = async (publishNow = false) => {
    setIsSubmitting(true);
    try {
      const payload = {
        criterion_scores: scores.map((c) => ({
          criterion_id: c.criterion_id,
          score: c.score,
        })),
        teacher_notes: teacherNotes,
        teacher_custom_feedback: teacherFeedback,
        approve: !publishNow,
        publish_now: publishNow,
      };

      const updated = await evaluationService.reviewEvaluation(evaluation.id, payload);
      
      if (publishNow) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
        });
        toast.success(`Result published successfully! Final Score: ${updated.total_score}/${updated.max_possible_score} (${updated.letter_grade})`);
      } else {
        toast.success('Evaluation review saved successfully.');
      }

      if (onEvaluationUpdated) {
        onEvaluationUpdated(updated);
      }
      onClose();
    } catch (err) {
      toast.error('Failed to update evaluation review.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Teacher Review & Approval"
      maxWidth="780px"
      footer={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Computed Total:</span>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary-500)' }}>
              {computedTotal.toFixed(1)} / {maxPossible} ({formatPercentage(computedPct)})
            </span>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Button variant="secondary" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              variant="secondary"
              icon={Save}
              onClick={() => handleSave(false)}
              isLoading={isSubmitting}
            >
              Save Draft
            </Button>
            <Button
              variant="success"
              icon={Award}
              onClick={() => handleSave(true)}
              isLoading={isSubmitting}
            >
              Approve & Publish Result
            </Button>
          </div>
        </div>
      }
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Review the AI-generated criterion scores below. You can adjust individual scores, modify comments, and approve for student publication.
        </p>

        {/* Live Criteria Editor */}
        <CriterionScorer
          criterionScores={scores}
          isEditable={true}
          onScoreChange={handleScoreChange}
        />

        {/* Notes */}
        <div className="form-group">
          <label className="form-label">Internal Teacher Review Notes (Optional)</label>
          <textarea
            rows={2}
            className="form-textarea"
            placeholder="Private notes for grading records..."
            value={teacherNotes}
            onChange={(e) => setTeacherNotes(e.target.value)}
          />
        </div>

        {/* Custom student feedback note */}
        <div className="form-group">
          <label className="form-label">Student-Facing Instructor Feedback (Optional)</label>
          <textarea
            rows={3}
            className="form-textarea"
            placeholder="Personal note visible to the student upon publication..."
            value={teacherFeedback}
            onChange={(e) => setTeacherFeedback(e.target.value)}
          />
        </div>
      </div>
    </Modal>
  );
};
