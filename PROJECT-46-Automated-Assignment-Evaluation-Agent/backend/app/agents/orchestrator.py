import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.assignment import Assignment
from backend.app.models.rubric import Rubric
from backend.app.models.evaluation import Evaluation, EvaluationStatus, EvaluationCriterionScore, AgentDecisionLog
from backend.app.models.originality import OriginalityReport
from backend.app.models.feedback import Feedback

from backend.app.services.document_extractor import document_extractor
from backend.app.services.rag_service import rag_service
from backend.app.services.originality_service import originality_service

from backend.app.agents.rubric_agent import rubric_agent
from backend.app.agents.evaluation_agent import evaluation_agent
from backend.app.agents.scoring_agent import scoring_agent
from backend.app.agents.feedback_agent import feedback_agent

logger = logging.getLogger(__name__)


class EvaluationOrchestrator:
    """Coordinates the entire multi-agent evaluation workflow, audit trail logging, and database state transitions."""

    async def run_evaluation_pipeline(
        self,
        db: Session,
        submission_id: int,
        triggered_by_user_id: Optional[int] = None
    ) -> Evaluation:
        """
        Executes the full agentic evaluation sequence for a given submission.
        Guarantees that results transition to 'UNDER_REVIEW' for mandatory teacher approval.
        """
        start_overall_time = time.time()
        
        # 1. Fetch submission and assignment
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise ValueError(f"Submission with ID #{submission_id} not found.")

        assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
        if not assignment:
            raise ValueError(f"Assignment with ID #{submission.assignment_id} not found.")

        # Check or find rubric
        rubric = db.query(Rubric).filter(Rubric.assignment_id == assignment.id).first()
        if not rubric or not rubric.criteria:
            raise ValueError(f"Assignment '{assignment.title}' has no rubric defined. A rubric is required for evaluation.")

        # Create or update evaluation record
        evaluation = db.query(Evaluation).filter(Evaluation.submission_id == submission.id).first()
        if not evaluation:
            evaluation = Evaluation(
                submission_id=submission.id,
                status=EvaluationStatus.EVALUATING,
                total_score=0.0,
                max_possible_score=rubric.total_points,
                percentage=0.0,
            )
            db.add(evaluation)
            db.flush()
        else:
            evaluation.status = EvaluationStatus.EVALUATING
            # Clear previous decision logs and scores for re-evaluation
            db.query(EvaluationCriterionScore).filter(EvaluationCriterionScore.evaluation_id == evaluation.id).delete()
            db.query(AgentDecisionLog).filter(AgentDecisionLog.evaluation_id == evaluation.id).delete()
            db.flush()

        submission.status = SubmissionStatus.EVALUATING
        db.commit()

        try:
            # ------------------------------------------------------------------
            # STAGE 1: DOCUMENT VALIDATION & EXTRACTION
            # ------------------------------------------------------------------
            t0 = time.time()
            if not submission.extracted_text or len(submission.extracted_text.strip()) < 10:
                extract_res = document_extractor.extract_text(submission.file_path, submission.file_type)
                submission.extracted_text = extract_res["text"]
                submission.word_count = extract_res["word_count"]
                submission.character_count = extract_res["character_count"]
                db.commit()

            text_len = len(submission.extracted_text)
            self._log_decision(
                db, evaluation.id,
                step_name="DOCUMENT_VALIDATION",
                agent_name="DocumentExtractorService",
                status="completed",
                details=f"Extracted and validated submission text ({submission.word_count} words, {text_len} characters).",
                exec_time_ms=int((time.time() - t0) * 1000)
            )

            # ------------------------------------------------------------------
            # STAGE 2: RUBRIC ANALYSIS
            # ------------------------------------------------------------------
            t0 = time.time()
            rubric_analysis = rubric_agent.analyze_rubric(rubric)
            self._log_decision(
                db, evaluation.id,
                step_name="RUBRIC_ANALYSIS",
                agent_name="RubricAnalysisAgent",
                status="completed",
                details=rubric_analysis["analysis_summary"],
                exec_time_ms=int((time.time() - t0) * 1000)
            )

            # ------------------------------------------------------------------
            # STAGE 3: RAG KNOWLEDGE INDEXING & RETRIEVAL
            # ------------------------------------------------------------------
            t0 = time.time()
            # Index assignment materials if not already indexed
            ref_docs_data = [
                {"title": doc.title, "content": doc.extracted_text or ""}
                for doc in assignment.reference_documents if doc.extracted_text
            ]
            guidelines_text = rubric_agent.generate_guidelines_text(rubric)
            indexed_chunks = rag_service.index_assignment_documents(
                assignment_id=assignment.id,
                assignment_title=assignment.title,
                instructions=assignment.instructions,
                reference_docs=ref_docs_data,
                rubric_guidelines=guidelines_text
            )
            self._log_decision(
                db, evaluation.id,
                step_name="RAG_RETRIEVAL",
                agent_name="RAGService",
                status="completed",
                details=f"Indexed and prepared {indexed_chunks} context chunks into ChromaDB collection 'assignment_{assignment.id}_knowledge'.",
                exec_time_ms=int((time.time() - t0) * 1000)
            )

            # ------------------------------------------------------------------
            # STAGE 4: CRITERION-LEVEL EVALUATION
            # ------------------------------------------------------------------
            t0 = time.time()
            raw_criterion_evals = await evaluation_agent.evaluate_criteria(
                assignment_id=assignment.id,
                assignment_title=assignment.title,
                criteria=rubric_analysis["criteria"],
                submission_text=submission.extracted_text
            )
            self._log_decision(
                db, evaluation.id,
                step_name="CRITERION_EVALUATION",
                agent_name="EvaluationAgent",
                status="completed",
                details=f"Evaluated {len(raw_criterion_evals)} criteria against rubric guidelines and retrieved context.",
                exec_time_ms=int((time.time() - t0) * 1000)
            )

            # ------------------------------------------------------------------
            # STAGE 5: ORIGINALITY & SIMILARITY ANALYSIS
            # ------------------------------------------------------------------
            t0 = time.time()
            orig_result = originality_service.analyze_similarity(
                db=db,
                submission_id=submission.id,
                assignment_id=assignment.id,
                submission_text=submission.extracted_text
            )
            
            # Save or update OriginalityReport
            orig_report = db.query(OriginalityReport).filter(OriginalityReport.submission_id == submission.id).first()
            if not orig_report:
                orig_report = OriginalityReport(
                    submission_id=submission.id,
                    similarity_percentage=orig_result["similarity_percentage"],
                    risk_level=orig_result["risk_level"],
                    status_label=orig_result["status_label"],
                    match_summary=orig_result["match_summary"],
                    matched_submission_count=orig_result["matched_submission_count"],
                    matches_json=orig_result["matches"],
                    disclaimer=orig_result["disclaimer"]
                )
                db.add(orig_report)
            else:
                orig_report.similarity_percentage = orig_result["similarity_percentage"]
                orig_report.risk_level = orig_result["risk_level"]
                orig_report.status_label = orig_result["status_label"]
                orig_report.match_summary = orig_result["match_summary"]
                orig_report.matched_submission_count = orig_result["matched_submission_count"]
                orig_report.matches_json = orig_result["matches"]
            db.flush()

            self._log_decision(
                db, evaluation.id,
                step_name="ORIGINALITY_ANALYSIS",
                agent_name="OriginalityService",
                status="completed",
                details=f"Computed originality metric: {orig_result['similarity_percentage']}% ({orig_result['status_label']}) across peer submissions.",
                exec_time_ms=int((time.time() - t0) * 1000)
            )

            # ------------------------------------------------------------------
            # STAGE 6: DETERMINISTIC SCORING ENGINE
            # ------------------------------------------------------------------
            t0 = time.time()
            scored_output = scoring_agent.compute_evaluation_score(
                criterion_evaluations=raw_criterion_evals,
                expected_total_points=rubric.total_points
            )

            evaluation.total_score = scored_output["total_score"]
            evaluation.max_possible_score = scored_output["max_possible_score"]
            evaluation.percentage = scored_output["percentage"]
            evaluation.letter_grade = scored_output["letter_grade"]

            # Save individual Criterion Scores
            for c_score in scored_output["criterion_scores"]:
                db_crit_score = EvaluationCriterionScore(
                    evaluation_id=evaluation.id,
                    criterion_id=c_score["criterion_id"],
                    criterion_name=c_score["criterion_name"],
                    score=c_score["score"],
                    max_points=c_score["max_points"],
                    percentage=c_score["percentage"],
                    rationale=c_score["rationale"],
                    evidence_quote=c_score["evidence_quote"]
                )
                db.add(db_crit_score)
            db.flush()

            self._log_decision(
                db, evaluation.id,
                step_name="SCORING_ARITHMETIC",
                agent_name="ScoringAgent",
                status="completed",
                details=f"Calculated programmatic total: {scored_output['total_score']}/{scored_output['max_possible_score']} ({scored_output['percentage']}%, Grade: {scored_output['letter_grade']}).",
                exec_time_ms=int((time.time() - t0) * 1000)
            )

            # ------------------------------------------------------------------
            # STAGE 7: PERSONALIZED FEEDBACK SYNTHESIS
            # ------------------------------------------------------------------
            t0 = time.time()
            student_name = submission.student.full_name if submission.student else f"Student #{submission.student_id}"
            feedback_data = await feedback_agent.generate_feedback(
                assignment_title=assignment.title,
                student_name=student_name,
                criterion_scores=scored_output["criterion_scores"],
                submission_text=submission.extracted_text,
                similarity_percentage=orig_result["similarity_percentage"]
            )

            evaluation.evaluation_summary = feedback_data["executive_summary"]
            evaluation.detailed_explanation = (
                f"Evaluation conducted across {len(scored_output['criterion_scores'])} criteria. "
                f"Total score: {scored_output['total_score']}/{scored_output['max_possible_score']} ({scored_output['percentage']}%). "
                f"Similarity index: {orig_result['similarity_percentage']}%."
            )

            # Save or update Feedback record
            fb_record = db.query(Feedback).filter(Feedback.evaluation_id == evaluation.id).first()
            if not fb_record:
                fb_record = Feedback(
                    evaluation_id=evaluation.id,
                    executive_summary=feedback_data["executive_summary"],
                    strengths_json=feedback_data["strengths"],
                    weaknesses_json=feedback_data["weaknesses"],
                    improvements_json=feedback_data["improvements"],
                    action_items_json=feedback_data.get("action_items", [])
                )
                db.add(fb_record)
            else:
                fb_record.executive_summary = feedback_data["executive_summary"]
                fb_record.strengths_json = feedback_data["strengths"]
                fb_record.weaknesses_json = feedback_data["weaknesses"]
                fb_record.improvements_json = feedback_data["improvements"]
                fb_record.action_items_json = feedback_data.get("action_items", [])
            db.flush()

            self._log_decision(
                db, evaluation.id,
                step_name="FEEDBACK_SYNTHESIS",
                agent_name="FeedbackAgent",
                status="completed",
                details="Synthesized strengths, areas for improvement, and actionable next steps.",
                exec_time_ms=int((time.time() - t0) * 1000)
            )

            # ------------------------------------------------------------------
            # STAGE 8: WORKFLOW STATE TRANSITION (AWAITING TEACHER REVIEW)
            # ------------------------------------------------------------------
            evaluation.status = EvaluationStatus.UNDER_REVIEW
            submission.status = SubmissionStatus.UNDER_REVIEW
            
            total_duration_ms = int((time.time() - start_overall_time) * 1000)
            self._log_decision(
                db, evaluation.id,
                step_name="AWAITING_TEACHER_REVIEW",
                agent_name="EvaluationOrchestrator",
                status="completed",
                details=f"Evaluation pipeline completed in {total_duration_ms}ms. Held for teacher review and approval.",
                exec_time_ms=total_duration_ms
            )

            db.commit()
            db.refresh(evaluation)
            logger.info(f"Evaluation pipeline succeeded for submission #{submission_id} -> Status: UNDER_REVIEW")
            return evaluation

        except Exception as e:
            db.rollback()
            logger.error(f"Evaluation pipeline failed for submission #{submission_id}: {str(e)}", exc_info=True)
            
            # Record failure state
            try:
                evaluation.status = EvaluationStatus.FAILED
                submission.status = SubmissionStatus.FAILED
                self._log_decision(
                    db, evaluation.id,
                    step_name="PIPELINE_ERROR",
                    agent_name="EvaluationOrchestrator",
                    status="failed",
                    details=f"Pipeline aborted: {str(e)}",
                    exec_time_ms=int((time.time() - start_overall_time) * 1000)
                )
                db.commit()
            except Exception:
                pass
            raise

    def _log_decision(
        self,
        db: Session,
        evaluation_id: int,
        step_name: str,
        agent_name: str,
        status: str,
        details: str,
        exec_time_ms: int = 0
    ):
        log_entry = AgentDecisionLog(
            evaluation_id=evaluation_id,
            step_name=step_name,
            agent_name=agent_name,
            status=status,
            details=details,
            execution_time_ms=exec_time_ms,
            created_at=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.flush()


orchestrator = EvaluationOrchestrator()
