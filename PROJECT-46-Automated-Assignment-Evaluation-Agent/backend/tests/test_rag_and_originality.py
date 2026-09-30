import pytest
from backend.app.services.rag_service import rag_service
from backend.app.services.originality_service import originality_service
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.assignment import Assignment, AssignmentStatus


def test_text_chunker():
    text = (
        "Paragraph 1 discusses the theoretical framework of machine learning. " * 5 + "\n\n" +
        "Paragraph 2 discusses empirical benchmarks and dataset partitioning. " * 5 + "\n\n" +
        "Paragraph 3 concludes the analysis with summary statistics and findings. " * 5
    )
    chunks = rag_service.chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) >= 3
    assert all(len(c) > 0 for c in chunks)


def test_originality_service_similarity(db_session, test_teacher, test_student):
    # Create an assignment
    assign = Assignment(
        title="Test Similarity Assignment",
        instructions="Instructions text",
        max_score=100.0,
        status=AssignmentStatus.ACTIVE,
        teacher_id=test_teacher.id
    )
    db_session.add(assign)
    db_session.flush()

    # Submission 1: Original text
    text_orig = "We implement a deep neural network with 4 layers using AdamW optimizer and evaluate on MNIST test dataset."
    sub1 = Submission(
        assignment_id=assign.id,
        student_id=test_student.id,
        file_name="sub1.txt",
        file_path="sub1.txt",
        file_type="txt",
        extracted_text=text_orig,
        status=SubmissionStatus.EXTRACTED
    )
    db_session.add(sub1)
    db_session.flush()

    # Submission 2: Very similar text
    text_copy = "We implement a deep neural network with 4 layers using AdamW optimizer and evaluate on MNIST test dataset with minor adjustments."
    sub2 = Submission(
        assignment_id=assign.id,
        student_id=test_student.id,
        file_name="sub2.txt",
        file_path="sub2.txt",
        file_type="txt",
        extracted_text=text_copy,
        status=SubmissionStatus.EXTRACTED
    )
    db_session.add(sub2)
    db_session.commit()

    # Run originality analysis on sub2 against corpus
    res = originality_service.analyze_similarity(db_session, sub2.id, assign.id, text_copy)
    assert res["similarity_percentage"] > 50.0
    assert res["risk_level"] in ("medium", "high")
    assert len(res["matches"]) >= 1
