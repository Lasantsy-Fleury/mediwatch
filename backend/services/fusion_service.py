from typing import Optional
from datetime import datetime
import uuid

# ---------------------------------------------------------------------------
# Service de fusion multimodale
# Combine les résultats des 3 services (texte, vitaux, image)
# en un résultat clinique unifié.
# ---------------------------------------------------------------------------

RISK_LEVEL_WEIGHTS = {
    "low":      0.2,
    "normal":   0.0,
    "medium":   0.5,
    "warning":  0.5,
    "high":     0.8,
    "critical": 1.0
}

def _merge_risk_scores(text_scores: list, vitals_score: float, image_risk: str) -> list:
    """
    Fusionne les scores de risque de toutes les modalités.
    Applique une pondération : texte 50%, vitaux 35%, image 15%.
    """
    merged = {}

    # Intégration des scores texte
    for score in text_scores:
        cat = score["category"]
        merged[cat] = {
            "category": cat,
            "label": score.get("label", cat),
            "score": score["score"] * 0.5,
            "level": score["level"],
            "sources": ["text"]
        }

    # Intégration du score vitaux (catégorie cardio + metabolic)
    if vitals_score > 0:
        for cat in ["cardio", "metabolic"]:
            if cat in merged:
                merged[cat]["score"] = min(1.0, merged[cat]["score"] + vitals_score * 0.35)
                merged[cat]["sources"].append("vitals")
            else:
                merged[cat] = {
                    "category": cat,
                    "label": "Cardio/Métabolique (constantes)",
                    "score": round(vitals_score * 0.35, 2),
                    "level": "warning" if vitals_score > 0.5 else "low",
                    "sources": ["vitals"]
                }

    # Intégration du risque image
    image_weight = RISK_LEVEL_WEIGHTS.get(image_risk, 0.0)
    if image_weight > 0:
        if "dermatological" not in merged:
            merged["dermatological"] = {
                "category": "dermatological",
                "label": "Risque dermatologique",
                "score": round(image_weight * 0.15, 2),
                "level": image_risk,
                "sources": ["image"]
            }

    # Recalcul des niveaux finaux
    result = []
    for cat_data in merged.values():
        score = cat_data["score"]
        if score >= 0.7:
            cat_data["level"] = "high"
        elif score >= 0.4:
            cat_data["level"] = "medium"
        else:
            cat_data["level"] = "low"
        cat_data["score"] = round(score, 2)
        result.append(cat_data)

    # Tri par score décroissant
    return sorted(result, key=lambda x: x["score"], reverse=True)


def _merge_alerts(text_alerts: list, vitals_alerts: list, image_alerts: list) -> list:
    """Fusionne et déduplique les alertes de toutes les modalités."""
    all_alerts = text_alerts + vitals_alerts + image_alerts
    # Tri : critical d'abord, puis warning
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    return sorted(all_alerts, key=lambda x: severity_order.get(x.get("severity", "info"), 2))


def fuse_analysis(
    patient_id: str,
    text_analysis: Optional[dict],
    vitals_analysis: Optional[dict],
    image_analysis: Optional[dict]
) -> dict:
    """
    Fusion multimodale principale.
    
    Args:
        patient_id: ID du patient
        text_analysis: Résultat de text_service.analyze_consultation_text()
        vitals_analysis: Résultat de timeseries_service.analyze_vitals()
        image_analysis: Résultat de image_service.analyze_image()
        
    Returns:
        ConsultationAnalysis dict complet prêt pour la réponse API
    """
    # Valeurs par défaut si une modalité est absente
    text_analysis = text_analysis or {
        "risk_scores": [], "alerts": [],
        "suggested_questions": [], "suggested_exams": [], "summary": ""
    }
    vitals_analysis = vitals_analysis or {
        "analyses": [], "global_level": "normal", "alerts": [], "score": 0.0
    }
    image_analysis = image_analysis or {
        "category": "no_image", "risk_level": "low",
        "alerts": [], "recommendations": []
    }

    # Fusion des scores de risque
    fused_risk_scores = _merge_risk_scores(
        text_scores=text_analysis.get("risk_scores", []),
        vitals_score=vitals_analysis.get("score", 0.0),
        image_risk=image_analysis.get("risk_level", "low")
    )

    # Fusion des alertes
    fused_alerts = _merge_alerts(
        text_alerts=text_analysis.get("alerts", []),
        vitals_alerts=vitals_analysis.get("alerts", []),
        image_alerts=image_analysis.get("alerts", [])
    )

    # Agrégation des suggestions
    suggested_questions = text_analysis.get("suggested_questions", [])
    suggested_exams = list(dict.fromkeys(
        text_analysis.get("suggested_exams", []) +
        image_analysis.get("recommendations", [])
    ))

    # Résumé global
    n_alerts = len(fused_alerts)
    n_risks = len([r for r in fused_risk_scores if r["level"] in ("medium", "high")])
    summary_parts = [text_analysis.get("summary", "")]

    if vitals_analysis.get("global_level") in ("warning", "critical"):
        summary_parts.append(f"Constantes vitales anormales (niveau : {vitals_analysis['global_level']}).")
    if image_analysis.get("category") not in ("normal", "no_image", "error"):
        summary_parts.append(f"Lésion détectée : {image_analysis.get('label', '')}.")

    summary = " ".join(filter(None, summary_parts))

    return {
        "consultation_id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "risk_scores": fused_risk_scores,
        "alerts": fused_alerts,
        "suggested_questions": suggested_questions,
        "suggested_exams": suggested_exams,
        "raw_text_analysis": text_analysis,
        "raw_vitals_analysis": vitals_analysis,
        "raw_image_analysis": image_analysis
    }