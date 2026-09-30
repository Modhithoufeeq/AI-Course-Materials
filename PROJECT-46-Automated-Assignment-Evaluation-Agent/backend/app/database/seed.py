import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.app.database.session import SessionLocal, init_db
from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole
from backend.app.models.assignment import Assignment, AssignmentStatus, ReferenceDocument
from backend.app.models.rubric import Rubric, RubricCriterion
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.core.config import settings


def seed_database():
    """Seed comprehensive initial demo data for testing the complete end-to-end workflow."""
    init_db()
    db: Session = SessionLocal()
    
    uploads_dir = Path(settings.UPLOAD_DIRECTORY) / "submissions"
    ref_dir = Path(settings.UPLOAD_DIRECTORY) / "references"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    ref_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "teacher@evalagent.com").first():
            print("Database already contains seed data. Skipping.")
            return

        print("Seeding Teacher and Student Users...")
        # 1. Teachers
        teacher = User(
            email="teacher@evalagent.com",
            hashed_password=get_password_hash("password123"),
            full_name="Dr. Alexander Wright",
            role=UserRole.TEACHER,
            department="Computer Science & Artificial Intelligence",
            is_active=True
        )
        db.add(teacher)
        db.flush()

        # 2. Students
        students = [
            User(email="student1@evalagent.com", hashed_password=get_password_hash("password123"), full_name="Rahul Sharma", role=UserRole.STUDENT, student_id="CS2025-01", department="Computer Science", is_active=True),
            User(email="student2@evalagent.com", hashed_password=get_password_hash("password123"), full_name="Sarah Jenkins", role=UserRole.STUDENT, student_id="CS2025-02", department="Data Science", is_active=True),
            User(email="student3@evalagent.com", hashed_password=get_password_hash("password123"), full_name="David Kim", role=UserRole.STUDENT, student_id="CS2025-03", department="Software Engineering", is_active=True),
            User(email="student4@evalagent.com", hashed_password=get_password_hash("password123"), full_name="Elena Rostova", role=UserRole.STUDENT, student_id="CS2025-04", department="Computer Science", is_active=True),
            User(email="student5@evalagent.com", hashed_password=get_password_hash("password123"), full_name="Marcus Vance", role=UserRole.STUDENT, student_id="CS2025-05", department="Artificial Intelligence", is_active=True),
        ]
        for s in students:
            db.add(s)
        db.flush()

        print("Seeding Assignment 1: Machine Learning Classifier...")
        # 3. Assignment 1
        assign1 = Assignment(
            title="Machine Learning Classifier & Model Evaluation",
            code="CS-501-A1",
            description="Build, train, and empirically evaluate a multi-class deep learning classifier with class imbalance mitigation and error analysis.",
            instructions="""
# Assignment Objectives:
1. Implement a clean machine learning pipeline including data preprocessing, train/test/validation split, and feature scaling.
2. Train a baseline Logistic Regression model followed by a Multi-layer Perceptron (MLP) or Random Forest Classifier.
3. Address class imbalance using SMOTE or focal loss re-weighting.
4. Provide comprehensive evaluation metrics: Precision, Recall, Macro-F1, ROC-AUC curve, and a normalized confusion matrix.
5. Perform ablation experiments on learning rates, batch sizes, and regularization.
6. Write a comprehensive technical report documenting methodology, results, error analysis, and conclusions.
""",
            max_score=100.0,
            due_date=datetime.now(timezone.utc) + timedelta(days=14),
            status=AssignmentStatus.ACTIVE,
            teacher_id=teacher.id,
            enrolled_students=students
        )
        db.add(assign1)
        db.flush()

        # Rubric for Assignment 1
        rubric1 = Rubric(
            assignment_id=assign1.id,
            title="ML Classifier Evaluation Rubric",
            description="Comprehensive grading standard for Machine Learning classification, error analysis, and coding quality.",
            total_points=100.0
        )
        db.add(rubric1)
        db.flush()

        criteria1_data = [
            ("Understanding & Problem Formulation", "Theoretical understanding of classifier concepts, loss functions, and dataset distribution.", 20.0, 0, "Evaluate whether the student clearly articulates problem formulation, loss function optimization, and architectural decisions."),
            ("Implementation & Methodology", "Correctness of ML pipeline, model training, hyperparameter tuning, and data preprocessing.", 30.0, 1, "Verify pipeline completeness, handling of data leakage, validation splits, and optimization loops."),
            ("Code Quality & Architecture", "Code modularity, clean naming conventions, type safety, and reproducibility.", 20.0, 2, "Check for modular functions, configuration encapsulation, docstrings, and clean coding standards."),
            ("Testing & Benchmark Validation", "Empirical evaluation with precision, recall, F1, ROC-AUC, and confusion matrices.", 15.0, 3, "Look for rigorous quantitative metrics, ablation studies, and comparative performance tables."),
            ("Documentation & Error Analysis", "Depth of discussion, failure case analysis, visual diagrams, and structured writeup.", 15.0, 4, "Assess qualitative error analysis, failure modes, and clear conclusion explanations."),
        ]
        for name, desc, max_p, idx, guide in criteria1_data:
            c = RubricCriterion(
                rubric_id=rubric1.id,
                name=name,
                description=desc,
                max_points=max_p,
                order_index=idx,
                evaluation_guidelines=guide
            )
            db.add(c)

        # Reference Material
        ref1_path = ref_dir / "ml_evaluation_reference_guidelines.txt"
        ref1_content = """Course Reference Guide: Standard ML Evaluation Standards
- In unbalanced datasets, overall accuracy is misleading. Macro-F1 and PR-AUC must be reported.
- Data scaling parameters must be fitted solely on the training split to prevent test set contamination.
- Cross-validation k=5 or stratified train-validation-test splits (70/15/15) are required for robust generalization.
- Neural network weights must use Xavier/He initialization with AdamW or SGD with momentum.
"""
        with open(ref1_path, "w", encoding="utf-8") as f:
            f.write(ref1_content)

        ref_doc = ReferenceDocument(
            assignment_id=assign1.id,
            title="Course Reference: Standard ML Evaluation Guidelines",
            file_name="ml_evaluation_reference_guidelines.txt",
            file_path=str(ref1_path),
            file_type="txt",
            extracted_text=ref1_content,
            is_vectorized=1
        )
        db.add(ref_doc)

        print("Seeding Sample Student Submissions for Assignment 1...")
        # Sample Submissions
        # 1. Rahul Sharma (Outstanding submission)
        sub1_file = uploads_dir / "rahul_sharma_ml_project.txt"
        sub1_text = """# Machine Learning Classifier Technical Report
Author: Rahul Sharma (CS2025-01)
Course: CS-501 Advanced Machine Learning

## 1. Problem Formulation & Concept Overview
This project investigates multi-class image and tabular classification under severe class imbalance.
We formulate the objective using cross-entropy loss augmented with class weighting to penalize minority misclassifications.
The mathematical formulation guarantees that gradients computed during backpropagation scale inversely with class frequency.

## 2. Methodology and Implementation
Our implementation pipeline consists of:
- Standardized data preprocessing: RobustScaler was fitted exclusively on the 70% training split.
- Model Architectures: We developed both a Baseline Random Forest (100 estimators) and a Deep Residual MLP (4 layers with BatchNorm, Dropout 0.3, and GELU activations).
- Optimization: AdamW optimizer (learning rate 1e-3, weight decay 1e-4) paired with CosineAnnealingLR scheduling.
- Class Imbalance: Applied SMOTE oversampling in conjunction with focal loss (gamma=2.0).

## 3. Code Architecture & Modularity
The codebase is structured into modular components: `dataset.py`, `model.py`, `trainer.py`, and `evaluate.py`.
Configuration parameters are encapsulated using Pydantic schema validation. All random seeds (seed=42) are explicitly locked for strict reproducibility.

## 4. Empirical Testing & Benchmark Results
We evaluated models across 5-fold Stratified Cross-Validation:
- Baseline Random Forest: Macro-F1 = 0.78, ROC-AUC = 0.84
- Deep Residual MLP + Focal Loss: Macro-F1 = 0.89, ROC-AUC = 0.94, Accuracy = 91.4%
A full confusion matrix indicates that false positives on minority Class 3 decreased by 42%.
Unit tests covering tensor dimension shapes and loss monotonicity passed with 100% assertion coverage.

## 5. Documentation & Failure Case Analysis
We analyzed top misclassified instances and identified boundary ambiguity near noisy cluster overlaps.
Future enhancements include exploring self-supervised contrastive pretraining.
"""
        with open(sub1_file, "w", encoding="utf-8") as f:
            f.write(sub1_text)

        sub1 = Submission(
            assignment_id=assign1.id,
            student_id=students[0].id,
            file_name="rahul_sharma_ml_project.txt",
            file_path=str(sub1_file),
            file_type="txt",
            file_size_bytes=len(sub1_text.encode("utf-8")),
            extracted_text=sub1_text,
            word_count=len(sub1_text.split()),
            character_count=len(sub1_text),
            status=SubmissionStatus.EXTRACTED,
        )
        db.add(sub1)

        # 2. Sarah Jenkins (Good submission)
        sub2_file = uploads_dir / "sarah_jenkins_classifier.txt"
        sub2_text = """# Assignment Report: Multi-class Classifier
Student: Sarah Jenkins (CS2025-02)

## 1. Problem Understanding
We aimed to build a classification pipeline for structured data. We explored different classification algorithms including Logistic Regression and Random Forests.

## 2. Implementation
We wrote Python scripts using Scikit-Learn and PyTorch. Data was cleaned by removing missing values and applying MinMax scaling.
The model was trained for 50 epochs using Stochastic Gradient Descent with learning rate 0.01.
We addressed class distribution by balancing class weights in the loss function.

## 3. Code Structure
The code is written in a Jupyter notebook with clearly commented functions and code cells.
Functions are provided for data loading, model definition, training loop, and plotting accuracy curves.

## 4. Results & Metrics
- Logistic Regression Accuracy: 74.5%
- Random Forest Accuracy: 84.2%, Macro-F1: 0.81
- Validation Loss steadily decreased without major overfitting.
Confusion matrix plots show high accuracy on the majority class but lower precision on class 2.

## 5. Discussion
The model works well overall. In the future we would like to try hyperparameter tuning and cross validation.
"""
        with open(sub2_file, "w", encoding="utf-8") as f:
            f.write(sub2_text)

        sub2 = Submission(
            assignment_id=assign1.id,
            student_id=students[1].id,
            file_name="sarah_jenkins_classifier.txt",
            file_path=str(sub2_file),
            file_type="txt",
            file_size_bytes=len(sub2_text.encode("utf-8")),
            extracted_text=sub2_text,
            word_count=len(sub2_text.split()),
            character_count=len(sub2_text),
            status=SubmissionStatus.EXTRACTED,
        )
        db.add(sub2)

        # 3. Marcus Vance (Submission with shared sentences for originality testing)
        sub3_file = uploads_dir / "marcus_vance_submission.txt"
        sub3_text = """# Machine Learning Classifier Report
Student: Marcus Vance (CS2025-05)

## 1. Overview
This project investigates multi-class image and tabular classification under severe class imbalance.
We formulate the objective using cross-entropy loss augmented with class weighting to penalize minority misclassifications.

## 2. Implementation Methodology
Our implementation pipeline consists of:
Standardized data preprocessing: RobustScaler was fitted exclusively on the 70% training split.
Model Architectures: We developed both a Baseline Random Forest and a Deep Residual MLP.
We applied SMOTE oversampling in conjunction with focal loss.

## 3. Code and Execution
The codebase is structured into modular components: dataset.py, model.py, trainer.py, and evaluate.py.
We ran tests and recorded results.

## 4. Evaluation
Random forest achieved 80% accuracy. The confusion matrix was plotted.
"""
        with open(sub3_file, "w", encoding="utf-8") as f:
            f.write(sub3_text)

        sub3 = Submission(
            assignment_id=assign1.id,
            student_id=students[4].id,
            file_name="marcus_vance_submission.txt",
            file_path=str(sub3_file),
            file_type="txt",
            file_size_bytes=len(sub3_text.encode("utf-8")),
            extracted_text=sub3_text,
            word_count=len(sub3_text.split()),
            character_count=len(sub3_text),
            status=SubmissionStatus.EXTRACTED,
        )
        db.add(sub3)

        db.commit()
        print("Database seeded successfully with Teacher, 5 Students, 1 Active Assignment, Rubric, and 3 Submissions!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
