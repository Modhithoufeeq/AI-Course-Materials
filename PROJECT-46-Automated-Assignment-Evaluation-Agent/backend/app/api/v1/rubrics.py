from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.rubric import Rubric, RubricCriterion
from backend.app.models.assignment import Assignment
from backend.app.schemas.rubric import RubricCreate, RubricUpdate, RubricResponse
from backend.app.api.deps import require_teacher, get_current_user

router = APIRouter()

STANDARD_TEMPLATES = [
    {
        "id": "cs_project",
        "title": "Computer Science & Engineering Project",
        "description": "Standard rubric for coding assignments, system design, and software projects.",
        "total_points": 100.0,
        "criteria": [
            {"name": "Understanding & Problem Analysis", "description": "Grasp of requirements, architecture, and conceptual principles.", "max_points": 20.0, "order_index": 0},
            {"name": "Implementation & Functional Correctness", "description": "Algorithm execution, edge-case handling, and feature completeness.", "max_points": 30.0, "order_index": 1},
            {"name": "Code Quality & Architecture", "description": "Modularity, naming conventions, clean code principles, and design patterns.", "max_points": 20.0, "order_index": 2},
            {"name": "Testing & Validation", "description": "Unit tests, integration tests, benchmark validation, and verification.", "max_points": 15.0, "order_index": 3},
            {"name": "Documentation & Presentation", "description": "Technical report, README instructions, inline documentation, and clarity.", "max_points": 15.0, "order_index": 4},
        ]
    },
    {
        "id": "research_essay",
        "title": "Academic Research Paper / Essay",
        "description": "Standard rubric for academic writing, essays, and literature reviews.",
        "total_points": 100.0,
        "criteria": [
            {"name": "Thesis & Conceptual Argument", "description": "Clarity of research objective and logical formulation of thesis.", "max_points": 25.0, "order_index": 0},
            {"name": "Evidence & Critical Analysis", "description": "Use of authoritative sources, quantitative data, and critical reasoning.", "max_points": 35.0, "order_index": 1},
            {"name": "Structure & Flow", "description": "Organization of paragraphs, logical transitions, and coherent narrative.", "max_points": 20.0, "order_index": 2},
            {"name": "Grammar, Style & Citations", "description": "Adherence to citation format (APA/IEEE), prose precision, and mechanics.", "max_points": 20.0, "order_index": 3},
        ]
    },
    {
        "id": "data_science_ml",
        "title": "Machine Learning & Data Science Report",
        "description": "Rubric tailored for model training, feature engineering, and performance evaluation.",
        "total_points": 100.0,
        "criteria": [
            {"name": "Exploratory Data Analysis", "description": "Data preprocessing, handling missing values, feature selection, and visualization.", "max_points": 25.0, "order_index": 0},
            {"name": "Model Architecture & Tuning", "description": "Selection of ML algorithms, hyperparameter tuning, and training pipeline.", "max_points": 30.0, "order_index": 1},
            {"name": "Evaluation & Error Analysis", "description": "Metrics analysis (Precision/Recall/F1/AUC), confusion matrices, and validation.", "max_points": 25.0, "order_index": 2},
            {"name": "Insights & Practical Discussion", "description": "Actionable takeaways, computational trade-offs, and conclusion.", "max_points": 20.0, "order_index": 3},
        ]
    }
]


@router.get("/templates", response_model=List[Dict[str, Any]])
def get_rubric_templates():
    """Return predefined standard academic rubric templates."""
    return STANDARD_TEMPLATES


@router.post("", response_model=RubricResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_rubric(
    rubric_in: RubricCreate,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    """Create or overwrite a rubric for an assignment."""
    if not rubric_in.assignment_id:
        raise HTTPException(status_code=400, detail="assignment_id is required.")

    assignment = db.query(Assignment).filter(Assignment.id == rubric_in.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    # Check if rubric already exists
    rubric = db.query(Rubric).filter(Rubric.assignment_id == rubric_in.assignment_id).first()
    if rubric:
        rubric.title = rubric_in.title
        rubric.description = rubric_in.description
        rubric.total_points = rubric_in.total_points
        # Clear existing criteria
        db.query(RubricCriterion).filter(RubricCriterion.rubric_id == rubric.id).delete()
    else:
        rubric = Rubric(
            assignment_id=rubric_in.assignment_id,
            title=rubric_in.title,
            description=rubric_in.description,
            total_points=rubric_in.total_points,
        )
        db.add(rubric)
        db.flush()

    for idx, c in enumerate(rubric_in.criteria):
        crit = RubricCriterion(
            rubric_id=rubric.id,
            name=c.name,
            description=c.description,
            max_points=c.max_points,
            weight=c.weight,
            order_index=idx,
            evaluation_guidelines=c.evaluation_guidelines,
        )
        db.add(crit)

    db.commit()
    db.refresh(rubric)
    return RubricResponse.model_validate(rubric)


@router.get("/{rubric_id}", response_model=RubricResponse)
def get_rubric(
    rubric_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retrieve rubric details and criteria."""
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found.")
    return RubricResponse.model_validate(rubric)
