from fastapi import APIRouter, HTTPException, status
from models.consultation import ConsultationCreate, VitalSigns
from models.response import APIResponse
from services.text_service import analyze_consultation_text
from services.timeseries_service import analyze_vitals
from services.image_service import analyze_image
from services.fusion_service import fuse_analysis
from utils.database import (
    get_patient_by_id,
    save_consultation,
    update_patient_risk_scores
)

router = APIRouter()


@router.post(
    "/consultation",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyser une nouvelle consultation"
)
async def create_consultation(consultation: ConsultationCreate):
    """
    Endpoint principal de MediWatch.
    Reçoit une consultation multimodale (texte + vitaux + image optionnelle),
    orchestre l'analyse via les services et retourne un résultat clinique fusionné.
    """

    # 1. Vérification que le patient existe
    patient = get_patient_by_id(consultation.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{consultation.patient_id}' introuvable"
        )

    # 2. Analyse textuelle (si note fournie)
    text_analysis = None
    if consultation.note_text:
        text_analysis = analyze_consultation_text(consultation.note_text)

    # 3. Analyse des constantes vitales (si vitaux fournis)
    vitals_analysis = None
    if consultation.vitals:
        vitals_analysis = analyze_vitals(consultation.vitals)

    # 4. Analyse image (si image fournie)
    image_analysis = None
    if consultation.image_base64:
        image_analysis = analyze_image(
            consultation.image_base64,
            consultation.image_description
        )

    # 5. Fusion multimodale des 3 analyses
    fused_result = fuse_analysis(
        patient_id=consultation.patient_id,
        text_analysis=text_analysis,
        vitals_analysis=vitals_analysis,
        image_analysis=image_analysis
    )

    # 6. Persistance en base mémoire
    saved = save_consultation(fused_result)

    # 7. Mise à jour des scores de risque du patient
    update_patient_risk_scores(
        consultation.patient_id,
        fused_result.get("risk_scores", [])
    )

    return APIResponse(
        success=True,
        data=saved,
        message="Consultation analysée avec succès"
    )


@router.get(
    "/consultation/{consultation_id}",
    response_model=APIResponse,
    summary="Récupérer une consultation par son ID"
)
async def get_consultation(consultation_id: str):
    """Retourne le détail complet d'une consultation analysée."""
    from utils.database import get_consultation_by_id
    consultation = get_consultation_by_id(consultation_id)
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation '{consultation_id}' introuvable"
        )
    return APIResponse(success=True, data=consultation)