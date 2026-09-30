import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Table
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

# Association table for student enrollment in assignments
assignment_students = Table(
    "assignment_students",
    Base.metadata,
    Column("assignment_id", Integer, ForeignKey("assignments.id", ondelete="CASCADE"), primary_key=True),
    Column("student_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class AssignmentStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)  # e.g., CS-401-A1
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=False)
    max_score = Column(Float, default=100.0, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.ACTIVE, nullable=False)
    
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    teacher = relationship("User", back_populates="created_assignments", foreign_keys=[teacher_id])
    rubrics = relationship("Rubric", back_populates="assignment", cascade="all, delete-orphan")
    reference_documents = relationship("ReferenceDocument", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    enrolled_students = relationship("User", secondary=assignment_students, lazy="joined")

    def __repr__(self):
        return f"<Assignment {self.id}: {self.title}>"


class ReferenceDocument(Base):
    __tablename__ = "reference_documents"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    extracted_text = Column(Text, nullable=True)
    is_vectorized = Column(Integer, default=0)  # 1 if indexed in ChromaDB
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    assignment = relationship("Assignment", back_populates="reference_documents")
