from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class VitalSigns(BaseModel):
    """
    Paramètres vitaux saisis lors d'une consultation.
    Tous les champs sont optionnels car le médecin peut ne pas
    mesurer tous les paramètres à chaque consultation.
    """
    systolic_bp: Optional[float] = Field(None, ge=50, le=300, description="Tension systolique (mmHg)")
    diastolic_bp: Optional[float] = Field(None, ge=30, le=200, description="Tension diastolique (mmHg)")
    heart_rate: Optional[float] = Field(None, ge=20, le=300, description="Fréquence cardiaque (bpm)")
    weight: Optional[float] = Field(None, ge=1, le=500, description="Poids (kg)")
    glucose: Optional[float] = Field(None, ge=0.5, le=50, description="Glycémie (mmol/L)")
    temperature: Optional[float] = Field(None, ge=33, le=45, description="Température (°C)")
    oxygen_saturation: Optional[float] = Field(None, ge=50, le=100, description="SpO2 (%)")

class ConsultationCreate(BaseModel):
    """
    Schéma d'entrée pour une nouvelle consultation.
    C'est ce que le frontend envoie au POST /consultation.
    """
    patient_id: str = Field(..., description="Identifiant unique du patient")
    note_text: Optional[str] = Field(None, max_length=5000, description="Note libre du médecin")
    vitals: Optional[VitalSigns] = Field(None, description="Paramètres vitaux mesurés")
    image_base64: Optional[str] = Field(None, description="Image de lésion encodée en base64")
    image_description: Optional[str] = Field(None, description="Description courte de l'image")

class ClinicalAlert(BaseModel):
    """Alerte clinique générée par le système"""
    type: str = Field(..., description="Ex: cardio, medication, followup")
    severity: str = Field(..., description="info, warning, critical")
    message: str
    recommendation: str

class ConsultationAnalysis(BaseModel):
    """
    Résultat de l'analyse d'une consultation.
    C'est ce que l'API retourne après traitement multimodal.
    """
    consultation_id: str
    patient_id: str
    timestamp: datetime
    summary: str = Field(..., description="Résumé structuré de la consultation")
    risk_scores: list = Field(default=[], description="Scores de risque mis à jour")
    alerts: List[ClinicalAlert] = Field(default=[])
    suggested_questions: List[str] = Field(default=[], description="Questions à poser au patient")
    suggested_exams: List[str] = Field(default=[], description="Bilans suggérés")
    raw_text_analysis: Optional[dict] = Field(None, description="Résultat brut du modèle NLP")
    raw_vitals_analysis: Optional[dict] = Field(None, description="Résultat brut de l'analyse des constantes")
    raw_image_analysis: Optional[dict] = Field(None, description="Résultat brut de l'analyse d'image")

class ConsultationRead(ConsultationCreate):
    """Schéma complet d'une consultation enregistrée"""
    id: str
    timestamp: datetime
    analysis: Optional[ConsultationAnalysis] = None

    class Config:
        from_attributes = True