from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    """
    Niveaux de risque clinique.
    Utiliser une Enum garantit que seules ces valeurs sont acceptées.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskScore(BaseModel):
    """Score de risque par catégorie clinique"""
    category: str = Field(..., description="Ex: cardio, metabolique, infectieux")
    level: RiskLevel
    score: float = Field(..., ge=0.0, le=1.0, description="Score normalisé entre 0 et 1")
    explanation: str = Field(..., description="Explication courte du score")

class Comorbidity(BaseModel):
    """Comorbidité connue d'un patient"""
    name: str = Field(..., description="Ex: diabète type 2, hypertension")
    since: Optional[str] = Field(None, description="Année de diagnostic")
    severity: Optional[str] = Field(None, description="légère, modérée, sévère")

class CurrentMedication(BaseModel):
    """Médicament en cours"""
    name: str
    dosage: str
    frequency: str = Field(..., description="Ex: 1x/jour, 2x/jour")

class PatientBase(BaseModel):
    """Données de base communes à la création et la lecture"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=130)
    gender: str = Field(..., pattern="^(M|F|Other)$")
    comorbidities: List[Comorbidity] = Field(default=[], description="Liste des comorbidités")
    current_medications: List[CurrentMedication] = Field(default=[])

class PatientCreate(PatientBase):
    """Schéma utilisé lors de la création d'un patient (POST)"""
    pass

class PatientRead(PatientBase):
    """Schéma utilisé lors de la lecture d'un patient (GET)"""
    id: str
    created_at: datetime
    risk_scores: List[RiskScore] = Field(default=[])

    class Config:
        from_attributes = True