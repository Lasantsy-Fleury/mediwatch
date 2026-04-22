from fastapi import APIRouter, HTTPException, status
from models.simulation import TreatmentHypothesis, SimulationResult, SimulatedDataPoint
from models.response import APIResponse
from utils.database import get_patient_by_id
import random
import math

router = APIRouter()


def _simulate_trajectory(
    patient: dict,
    hypothesis: TreatmentHypothesis
) -> list:
    """
    Simule la trajectoire d'un paramètre vital sur N jours.
    Utilise un modèle mathématique simple (décroissance exponentielle amortie)
    combiné aux comorbidités du patient.
    Sera remplacé par un vrai modèle LSTM dans les notebooks.
    """
    param = hypothesis.target_parameter or "systolic_bp"
    duration = hypothesis.duration_days
    description = hypothesis.treatment_hypothesis.lower()

    # Valeur de départ basée sur les constantes connues du patient
    start_values = {
        "systolic_bp": 155.0,
        "diastolic_bp": 95.0,
        "heart_rate": 88.0,
        "glucose": 8.5,
        "weight": 82.0
    }

    # Impact du traitement selon les mots-clés de l'hypothèse
    treatment_effects = {
        "antihypertenseur": {"systolic_bp": -18, "diastolic_bp": -10},
        "iec":              {"systolic_bp": -15, "diastolic_bp": -8},
        "bêtabloquant":     {"heart_rate": -15, "systolic_bp": -10},
        "betabloquant":     {"heart_rate": -15, "systolic_bp": -10},
        "insuline":         {"glucose": -2.5},
        "metformine":       {"glucose": -1.5},
        "diurétique":       {"systolic_bp": -12, "weight": -2},
        "diuretique":       {"systolic_bp": -12, "weight": -2},
    }

    # Calcul de l'effet total selon les mots du traitement
    total_effect = 0.0
    for keyword, effects in treatment_effects.items():
        if keyword in description:
            total_effect += effects.get(param, 0)

    # Si aucun effet trouvé, effet neutre léger
    if total_effect == 0:
        total_effect = -5.0

    start_value = start_values.get(param, 100.0)
    points = []

    for day in range(duration + 1):
        # Modèle : décroissance exponentielle + bruit gaussien
        progress = 1 - math.exp(-day / (duration * 0.4))
        trend = start_value + (total_effect * progress)
        noise = random.gauss(0, abs(total_effect) * 0.05)
        predicted = round(trend + noise, 1)

        # Intervalle de confiance (±5% de la valeur)
        margin = abs(predicted * 0.05)
        points.append(SimulatedDataPoint(
            day=day,
            parameter=param,
            predicted_value=predicted,
            confidence_lower=round(predicted - margin, 1),
            confidence_upper=round(predicted + margin, 1)
        ))

    return points


@router.post(
    "/simulate-treatment",
    response_model=APIResponse,
    summary="Simuler la trajectoire d'un patient sous hypothèse de traitement"
)
async def simulate_treatment(hypothesis: TreatmentHypothesis):
    """
    Simule l'évolution d'un paramètre vital sur N jours
    sous une hypothèse de changement de traitement.
    """

    # Vérification patient
    patient = get_patient_by_id(hypothesis.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{hypothesis.patient_id}' introuvable"
        )

    # Simulation de la trajectoire
    trajectory = _simulate_trajectory(patient, hypothesis)

    # Calcul du risque de décompensation
    # Basé sur la valeur finale vs seuil critique
    final_value = trajectory[-1].predicted_value if trajectory else 0
    param = hypothesis.target_parameter or "systolic_bp"

    critical_thresholds = {
        "systolic_bp": 160,
        "diastolic_bp": 100,
        "heart_rate": 120,
        "glucose": 11.1,
        "weight": 999
    }

    critical_threshold = critical_thresholds.get(param, 999)
    decompensation_risk = min(1.0, max(0.0, (final_value - critical_threshold * 0.8) / critical_threshold))
    decompensation_risk = round(decompensation_risk, 2)

    # Jour estimé de décompensation
    decompensation_day = None
    if decompensation_risk > 0.7:
        for point in trajectory:
            if point.predicted_value >= critical_threshold:
                decompensation_day = point.day
                break

    # Génération du narratif
    direction = "diminue" if trajectory[-1].predicted_value < trajectory[0].predicted_value else "augmente"
    delta = round(abs(trajectory[-1].predicted_value - trajectory[0].predicted_value), 1)
    narrative = (
        f"Sous l'hypothèse « {hypothesis.treatment_hypothesis} », "
        f"le paramètre {param} {direction} de {delta} unités "
        f"sur {hypothesis.duration_days} jours. "
        f"Risque de décompensation estimé : {int(decompensation_risk * 100)}%."
    )

    warnings = []
    if decompensation_risk > 0.7:
        warnings.append(f"⚠️ Risque élevé de décompensation détecté au jour {decompensation_day}")
    if decompensation_risk > 0.4:
        warnings.append("Surveillance rapprochée recommandée toutes les 72h")

    result = SimulationResult(
        patient_id=hypothesis.patient_id,
        treatment_description=hypothesis.treatment_hypothesis,
        duration_days=hypothesis.duration_days,
        trajectory=trajectory,
        decompensation_risk=decompensation_risk,
        decompensation_day=decompensation_day,
        narrative=narrative,
        warnings=warnings
    )

    return APIResponse(
        success=True,
        data=result.model_dump(),
        message="Simulation générée avec succès"
    )