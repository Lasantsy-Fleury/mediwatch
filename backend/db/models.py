"""
Modèles SQLAlchemy — définissent la structure des tables PostgreSQL.
Ces classes sont différentes des modèles Pydantic :
- Pydantic : validation des données API (entrée/sortie JSON)
- SQLAlchemy : mapping objet-relationnel (persistance en base)
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.session import Base
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())


class UserDB(Base):
    """Table des utilisateurs (médecins, admins)."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="doctor")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PatientDB(Base):
    """Table des patients."""
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=generate_uuid)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)

    # Données JSON pour les structures complexes
    # Plus flexible que des tables relationnelles pour ce type de données
    comorbidities = Column(JSON, default=list)
    current_medications = Column(JSON, default=list)
    risk_scores = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relation one-to-many avec consultations
    consultations = relationship(
        "ConsultationDB",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


class ConsultationDB(Base):
    """Table des consultations avec leurs analyses."""
    __tablename__ = "consultations"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)

    # Données de la consultation
    note_text = Column(Text, nullable=True)
    image_description = Column(String(500), nullable=True)

    # Paramètres vitaux
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)
    heart_rate = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    glucose = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    oxygen_saturation = Column(Float, nullable=True)

    # Résultats de l'analyse ML (stockés en JSON)
    analysis_summary = Column(Text, nullable=True)
    risk_scores = Column(JSON, default=list)
    alerts = Column(JSON, default=list)
    suggested_questions = Column(JSON, default=list)
    suggested_exams = Column(JSON, default=list)
    raw_text_analysis = Column(JSON, nullable=True)
    raw_vitals_analysis = Column(JSON, nullable=True)
    raw_image_analysis = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation many-to-one avec patient
    patient = relationship("PatientDB", back_populates="consultations")