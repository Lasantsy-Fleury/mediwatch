from fastapi import APIRouter, HTTPException, status
from models.patient import PatientCreate
from models.response import APIResponse
from utils.database import (
    get_all_patients,
    get_patient_by_id,
    create_patient,
    get_consultations_by_patient
)

router = APIRouter()


@router.get(
    "/patients",
    response_model=APIResponse,
    summary="Lister tous les patients"
)
async def list_patients():
    """Retourne la liste complète des patients enregistrés."""
    patients = get_all_patients()
    return APIResponse(
        success=True,
        data=patients,
        message=f"{len(patients)} patient(s) trouvé(s)"
    )


@router.get(
    "/patient/{patient_id}",
    response_model=APIResponse,
    summary="Récupérer un patient par son ID"
)
async def get_patient(patient_id: str):
    """Retourne les données complètes d'un patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' introuvable"
        )
    return APIResponse(success=True, data=patient)


@router.get(
    "/patient/{patient_id}/timeline",
    response_model=APIResponse,
    summary="Récupérer la timeline clinique d'un patient"
)
async def get_patient_timeline(patient_id: str):
    """
    Retourne l'historique structuré du patient :
    - Données patient (comorbidités, traitements)
    - Liste chronologique de toutes ses consultations
    - Scores de risque actuels
    """
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' introuvable"
        )

    consultations = get_consultations_by_patient(patient_id)

    # Tri chronologique des consultations
    consultations_sorted = sorted(
        consultations,
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )

    timeline = {
        "patient": patient,
        "consultations": consultations_sorted,
        "total_consultations": len(consultations_sorted),
        "risk_scores": patient.get("risk_scores", []),
        "last_updated": consultations_sorted[0].get("timestamp") if consultations_sorted else None
    }

    return APIResponse(
        success=True,
        data=timeline,
        message=f"Timeline de {patient['first_name']} {patient['last_name']}"
    )


@router.post(
    "/patient",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau patient"
)
async def create_new_patient(patient: PatientCreate):
    """Enregistre un nouveau patient dans le système."""
    patient_data = patient.model_dump()
    created = create_patient(patient_data)
    return APIResponse(
        success=True,
        data=created,
        message=f"Patient {created['first_name']} {created['last_name']} créé avec succès"
    )