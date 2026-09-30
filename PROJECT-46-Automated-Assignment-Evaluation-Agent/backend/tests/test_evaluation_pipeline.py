import pytest
from fastapi.testclient import TestClient
from backend.app.models.assignment import Assignment, AssignmentStatus
from backend.app.models.rubric import Rubric, RubricCriterion
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.evaluation import EvaluationStatus


def test_full_evaluation_and_teacher_approval_flow(
    client: TestClient, db_session, test_teacher, test_student, teacher_auth_headers
):
    # 1. Create an assignment
    assign = Assignment(
        title="Test End-to-End ML Pipeline",
        code="CS-TEST-1",
        description="Build classifier",
        instructions="Train MLP and report F1 score.",
        max_score=100.0,
        status=AssignmentStatus.ACTIVE,
        teacher_id=test_teacher.id
    )
    db_session.add(assign)
    db_session.flush()

    # 2. Add Rubric
    rubric = Rubric(assignment_id=assign.id, title="Test Rubric", total_points=100.0)
    db_session.add(rubric)
    db_session.flush()

    c1 = RubricCriterion(rubric_id=rubric.id, name="Understanding", max_points=40.0, order_index=0)
    c2 = RubricCriterion(rubric_id=rubric.id, name="Implementation", max_points=60.0, order_index=1)
    db_session.add_all([c1, c2])
    db_session.flush()

    # 3. Create a Submission
    sub_text = "In this assignment we implement a multilayer perceptron classifier using PyTorch. We evaluate with precision and recall metrics."
    sub = Submission(
        assignment_id=assign.id,
        student_id=test_student.id,
        file_name="student_test.txt",
        file_path="student_test.txt",
        file_type="txt",
        extracted_text=sub_text,
        word_count=len(sub_text.split()),
        character_count=len(sub_text),
        status=SubmissionStatus.EXTRACTED
    )
    db_session.add(sub)
    db_session.commit()

    # 4. Trigger AI Evaluation via API
    eval_resp = client.post(f"/api/v1/evaluations/{sub.id}/start", headers=teacher_auth_headers)
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    
    assert eval_data["status"] == "under_review"
    assert eval_data["total_score"] > 0
    assert len(eval_data["criterion_scores"]) == 2
    assert eval_data["originality_report"] is not None
    assert eval_data["feedback"] is not None
    assert len(eval_data["decision_logs"]) >= 7

    eval_id = eval_data["id"]

    # 5. Teacher Reviews and Modifies Score
    review_payload = {
        "criterion_scores": [
            {"criterion_id": c1.id, "score": 38.0, "teacher_comment": "Excellent conceptual clarity."},
            {"criterion_id": c2.id, "score": 54.0, "teacher_comment": "Solid implementation."}
        ],
        "teacher_notes": "Great effort on this test submission.",
        "teacher_custom_feedback": "Focus on optimizing model training speed in the future.",
        "approve": False
    }
    review_resp = client.put(f"/api/v1/evaluations/{eval_id}/review", json=review_payload, headers=teacher_auth_headers)
    assert review_resp.status_code == 200
    reviewed_data = review_resp.json()
    assert reviewed_data["total_score"] == 92.0  # 38 + 54 = 92.0
    assert reviewed_data["percentage"] == 92.0
    assert reviewed_data["letter_grade"] == "A-"

    # 6. Teacher Approves & Publishes
    approve_payload = {
        "teacher_notes": "Approved for grade publication.",
        "publish_to_student": True
    }
    approve_resp = client.post(f"/api/v1/evaluations/{eval_id}/approve", json=approve_payload, headers=teacher_auth_headers)
    assert approve_resp.status_code == 200
    approved_data = approve_resp.json()
    assert approved_data["status"] == "published"

    # 7. Check Published Result
    results_resp = client.get("/api/v1/results", headers=teacher_auth_headers)
    assert results_resp.status_code == 200
    assert len(results_resp.json()) >= 1
    assert results_resp.json()[0]["final_score"] == 92.0
