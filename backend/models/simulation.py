from pydantic import BaseModel, Field
from typing import List, Optional


class TreatmentHypothesis(BaseModel):
    """
    Hypothèse de traitement soumise pour simulation.
    """
    patient_id: str
    treatment_hypothesis: str = Field(
        ...,
        description="Ex: Ajout d'un IEC 5mg/jour pour HTA"
    )
    duration_days: int = Field(
        default=21,
        ge=1,
        le=365,
        description="Durée de simulation en jours"
    )
    target_parameter: Optional[str] = Field(
        None,
        description="Paramètre à surveiller : systolic_bp, glucose, weight..."
    )


class SimulatedDataPoint(BaseModel):
    """Point de données simulé sur la trajectoire."""
    day: int
    parameter: str
    predicted_value: float
    confidence_lower: float
    confidence_upper: float


class SimulationResult(BaseModel):
    """Résultat complet d'une simulation de trajectoire."""
    patient_id: str
    treatment_description: str
    duration_days: int
    trajectory: List[SimulatedDataPoint]
    decompensation_risk: float = Field(..., ge=0, le=1)
    decompensation_day: Optional[int] = Field(
        None,
        description="Jour estimé de décompensation si risque > 0.7"
    )
    narrative: str = Field(..., description="Explication en langage naturel")
    warnings: List[str] = Field(default=[])