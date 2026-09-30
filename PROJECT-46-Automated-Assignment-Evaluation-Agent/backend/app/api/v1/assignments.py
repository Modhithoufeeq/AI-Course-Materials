from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.assignment import Assignment, AssignmentStatus, ReferenceDocument
from backend.app.models.rubric import Rubric, RubricCriterion
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse, ReferenceDocumentResponse
from backend.app.api.deps import get_current_user, require_teacher
from backend.app.services.storage_service import storage_service
from backend.app.services.document_extractor import document_extractor
from backend.app.services.rag_service import rag_service

router = APIRouter()


@router.get("", response_model=List[AssignmentResponse])
def list_assignments(
    status_filter: Optional[AssignmentStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List assignments. Teachers see their created assignments; Students see assignments they are enrolled in."""
    query = db.query(Assignment)
    
    if current_user.role == UserRole.TEACHER:
        query = query.filter(Assignment.teacher_id == current_user.id)
    elif current_user.role == UserRole.STUDENT:
        query = query.filter(
            (Assignment.enrolled_students.any(User.id == current_user.id)) |
            (Assignment.status == AssignmentStatus.ACTIVE)
        )
    
    if status_filter:
        query = query.filter(Assignment.status == status_filter)
        
    assignments = query.order_by(Assignment.created_at.desc()).all()
    
    # Calculate submission counts
    results = []
    for a in assignments:
        resp = AssignmentResponse.model_validate(a)
        resp.submission_count = len(a.submissions)
        resp.evaluated_count = len([s for s in a.submissions if s.status in (SubmissionStatus.EVALUATED, SubmissionStatus.UNDER_REVIEW, SubmissionStatus.APPROVED, SubmissionStatus.PUBLISHED)])
        results.append(resp)
        
    return results


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    assign_in: AssignmentCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Create an assignment along with its rubric criteria and enrolled students."""
    assignment = Assignment(
        title=assign_in.title,
        code=assign_in.code,
        description=assign_in.description,
        instructions=assign_in.instructions,
        max_score=assign_in.max_score,
        due_date=assign_in.due_date,
        status=assign_in.status,
        teacher_id=teacher.id,
    )
    db.add(assignment)
    db.flush()

    # Create associated Rubric if criteria provided or generate standard default
    criteria_data = assign_in.rubric_criteria or [
        {"name": "Understanding & Analysis", "description": "Grasp of core concepts", "max_points": 25.0, "order_index": 0},
        {"name": "Implementation & Methodology", "description": "Correctness and execution", "max_points": 35.0, "order_index": 1},
        {"name": "Quality & Structure", "description": "Clarity, efficiency, standard practices", "max_points": 20.0, "order_index": 2},
        {"name": "Testing & Documentation", "description": "Verification and explanations", "max_points": 20.0, "order_index": 3},
    ]

    total_pts = sum(c.get("max_points", 0) if isinstance(c, dict) else c.max_points for c in criteria_data)
    
    rubric = Rubric(
        assignment_id=assignment.id,
        title=assign_in.rubric_title or f"Rubric for {assignment.title}",
        total_points=total_pts or assignment.max_score,
    )
    db.add(rubric)
    db.flush()

    for idx, c in enumerate(criteria_data):
        if isinstance(c, dict):
            name = c["name"]
            desc = c.get("description", "")
            max_p = c["max_points"]
            guidelines = c.get("evaluation_guidelines", "")
        else:
            name = c.name
            desc = c.description
            max_p = c.max_points
            guidelines = c.evaluation_guidelines

        criterion = RubricCriterion(
            rubric_id=rubric.id,
            name=name,
            description=desc,
            max_points=max_p,
            order_index=idx,
            evaluation_guidelines=guidelines
        )
        db.add(criterion)

    # Enroll students if IDs provided
    if assign_in.enrolled_student_ids:
        students = db.query(User).filter(User.id.in_(assign_in.enrolled_student_ids)).all()
        assignment.enrolled_students = students

    db.commit()
    db.refresh(assignment)

    resp = AssignmentResponse.model_validate(assignment)
    resp.submission_count = 0
    resp.evaluated_count = 0
    return resp


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment_detail(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full details of an assignment including rubric and reference documents."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    resp = AssignmentResponse.model_validate(assignment)
    resp.submission_count = len(assignment.submissions)
    resp.evaluated_count = len([s for s in assignment.submissions if s.status in (SubmissionStatus.EVALUATED, SubmissionStatus.UNDER_REVIEW, SubmissionStatus.APPROVED, SubmissionStatus.PUBLISHED)])
    return resp


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assign_in: AssignmentUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Update assignment metadata and instructions."""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or unauthorized.")

    if assign_in.title is not None:
        assignment.title = assign_in.title
    if assign_in.code is not None:
        assignment.code = assign_in.code
    if assign_in.description is not None:
        assignment.description = assign_in.description
    if assign_in.instructions is not None:
        assignment.instructions = assign_in.instructions
    if assign_in.max_score is not None:
        assignment.max_score = assign_in.max_score
    if assign_in.due_date is not None:
        assignment.due_date = assign_in.due_date
    if assign_in.status is not None:
        assignment.status = assign_in.status

    if assign_in.enrolled_student_ids is not None:
        students = db.query(User).filter(User.id.in_(assign_in.enrolled_student_ids)).all()
        assignment.enrolled_students = students

    db.commit()
    db.refresh(assignment)
    return AssignmentResponse.model_validate(assignment)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Delete an assignment and its related rubrics, submissions, and vector indexes."""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or unauthorized.")

    db.delete(assignment)
    db.commit()
    return None


@router.post("/{assignment_id}/references", response_model=ReferenceDocumentResponse)
async def upload_reference_document(
    assignment_id: int,
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Upload reference material / solution guides for RAG grounding."""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or unauthorized.")

    # Save file to disk
    file_path, original_name, size_bytes, file_type = await storage_service.save_upload_file(file, subfolder="references")
    
    # Extract text
    extracted_text = ""
    try:
        ext_res = document_extractor.extract_text(file_path, file_type)
        extracted_text = ext_res["text"]
    except Exception as e:
        logger.warning(f"Could not extract text from reference document: {e}")

    ref_doc = ReferenceDocument(
        assignment_id=assignment.id,
        title=title,
        file_name=original_name,
        file_path=file_path,
        file_type=file_type,
        extracted_text=extracted_text,
        is_vectorized=1 if extracted_text else 0
    )
    db.add(ref_doc)
    db.commit()
    db.refresh(ref_doc)

    return ReferenceDocumentResponse.model_validate(ref_doc)
