from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.assignment import Assignment
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.evaluation import Evaluation
from backend.app.schemas.submission import SubmissionResponse, SubmissionUploadResponse
from backend.app.api.deps import get_current_user
from backend.app.services.storage_service import storage_service
from backend.app.services.document_extractor import document_extractor

router = APIRouter()


@router.post("/upload", response_model=SubmissionUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_submission(
    assignment_id: int = Form(...),
    student_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a student assignment submission file (PDF, DOCX, TXT),
    extract and validate text content, and prepare it for agentic evaluation.
    """
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    # Determine target student
    if current_user.role == UserRole.TEACHER:
        target_student_id = student_id or current_user.id
    else:
        target_student_id = current_user.id

    # 1. Save upload file securely
    file_path, original_filename, file_size, file_type = await storage_service.save_upload_file(file, subfolder="submissions")

    # 2. Extract text immediately
    extracted_text = None
    extraction_error = None
    word_count = 0
    char_count = 0
    preview = None
    initial_status = SubmissionStatus.EXTRACTED

    try:
        ext_result = document_extractor.extract_text(file_path, file_type)
        extracted_text = ext_result["text"]
        word_count = ext_result["word_count"]
        char_count = ext_result["character_count"]
        preview = ext_result["preview"]
    except Exception as e:
        extraction_error = str(e)
        initial_status = SubmissionStatus.FAILED

    # 3. Create or replace Submission in DB
    submission = Submission(
        assignment_id=assignment_id,
        student_id=target_student_id,
        file_name=original_filename,
        file_path=file_path,
        file_type=file_type,
        file_size_bytes=file_size,
        extracted_text=extracted_text,
        word_count=word_count,
        character_count=char_count,
        extraction_error=extraction_error,
        status=initial_status,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return SubmissionUploadResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        file_name=submission.file_name,
        file_type=submission.file_type,
        file_size_bytes=submission.file_size_bytes,
        status=submission.status,
        word_count=submission.word_count,
        character_count=submission.character_count,
        submitted_at=submission.submitted_at,
        extraction_preview=preview or (f"Extraction issue: {extraction_error}" if extraction_error else "Empty preview")
    )


@router.get("", response_model=List[SubmissionResponse])
def list_submissions(
    assignment_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status_filter: Optional[SubmissionStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List submissions with filtering. Students are restricted to their own submissions."""
    query = db.query(Submission)

    if current_user.role == UserRole.STUDENT:
        query = query.filter(Submission.student_id == current_user.id)
    elif student_id:
        query = query.filter(Submission.student_id == student_id)

    if assignment_id:
        query = query.filter(Submission.assignment_id == assignment_id)

    if status_filter:
        query = query.filter(Submission.status == status_filter)

    submissions = query.order_by(Submission.submitted_at.desc()).all()
    
    results = []
    for s in submissions:
        resp = SubmissionResponse.model_validate(s)
        if s.evaluation:
            resp.evaluation_id = s.evaluation.id
            resp.total_score = s.evaluation.total_score
            resp.max_possible_score = s.evaluation.max_possible_score
        if s.originality_report:
            resp.similarity_percentage = s.originality_report.similarity_percentage
        results.append(resp)
        
    return results


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full details and extracted text of a submission."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only access your own submissions.")

    resp = SubmissionResponse.model_validate(submission)
    if submission.evaluation:
        resp.evaluation_id = submission.evaluation.id
        resp.total_score = submission.evaluation.total_score
        resp.max_possible_score = submission.evaluation.max_possible_score
    if submission.originality_report:
        resp.similarity_percentage = submission.originality_report.similarity_percentage
        
    return resp


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a submission."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this submission.")

    db.delete(submission)
    db.commit()
    return None
