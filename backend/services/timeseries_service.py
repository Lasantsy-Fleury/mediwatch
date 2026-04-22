from typing import Optional
from models.consultation import VitalSigns

# ---------------------------------------------------------------------------
# Seuils cliniques de référence (adulte standard)
# Source : recommandations HAS / ESC / ADA
# ---------------------------------------------------------------------------

VITAL_THRESHOLDS = {
    "systolic_bp": {
        "normal":   (90, 130),
        "warning":  (130, 160),
        "critical": (160, 300),
        "low":      (50, 90),
        "label":    "Tension systolique (mmHg)"
    },
    "diastolic_bp": {
        "normal":   (60, 85),
        "warning":  (85, 100),
        "critical": (100, 200),
        "low":      (30, 60),
        "label":    "Tension diastolique (mmHg)"
    },
    "heart_rate": {
        "normal":   (60, 100),
        "warning":  (100, 120),
        "critical": (120, 300),
        "low":      (20, 60),
        "label":    "Fréquence cardiaque (bpm)"
    },
    "glucose": {
        "normal":   (3.9, 7.8),
        "warning":  (7.8, 11.1),
        "critical": (11.1, 50),
        "low":      (0.5, 3.9),
        "label":    "Glycémie (mmol/L)"
    },
    "temperature": {
        "normal":   (36.1, 37.5),
        "warning":  (37.5, 39.0),
        "critical": (39.0, 45.0),
        "low":      (33.0, 36.1),
        "label":    "Température (°C)"
    },
    "oxygen_saturation": {
        "normal":   (95, 100),
        "warning":  (90, 95),
        "critical": (50, 90),
        "low":      (50, 90),
        "label":    "SpO2 (%)"
    }
}


def _classify_value(param: str, value: float) -> dict:
    """
    Classifie une valeur selon les seuils cliniques.
    Retourne un dict avec level, message et recommendation.
    """
    thresholds = VITAL_THRESHOLDS.get(param)
    if not thresholds:
        return {"level": "unknown", "message": "Paramètre non référencé", "recommendation": ""}

    label = thresholds["label"]
    normal_min, normal_max = thresholds["normal"]
    warn_min, warn_max = thresholds["warning"]
    crit_min, crit_max = thresholds["critical"]
    low_min, low_max = thresholds["low"]

    if normal_min <= value <= normal_max:
        return {
            "level": "normal",
            "message": f"{label} normale : {value}",
            "recommendation": ""
        }
    elif warn_min <= value < warn_max:
        return {
            "level": "warning",
            "message": f"{label} élevée : {value}",
            "recommendation": f"Surveiller et recontrôler dans 15 min"
        }
    elif value >= crit_min:
        return {
            "level": "critical",
            "message": f"{label} critique : {value}",
            "recommendation": f"Action immédiate requise — {label} à {value}"
        }
    elif low_min <= value < low_max:
        return {
            "level": "low",
            "message": f"{label} basse : {value}",
            "recommendation": f"Valeur basse à surveiller"
        }
    else:
        return {
            "level": "unknown",
            "message": f"{label} hors plage connue : {value}",
            "recommendation": "Vérifier la mesure"
        }


def analyze_vitals(vitals: VitalSigns) -> dict:
    """
    Analyse complète des paramètres vitaux d'une consultation.
    
    Args:
        vitals: Objet VitalSigns avec les mesures du patient
        
    Returns:
        dict avec keys: analyses, global_level, alerts, score
    """
    vitals_dict = vitals.model_dump(exclude_none=True)

    if not vitals_dict:
        return {
            "analyses": [],
            "global_level": "normal",
            "alerts": [],
            "score": 0.0
        }

    analyses = []
    alerts = []
    level_weights = {"normal": 0, "low": 1, "warning": 2, "critical": 3}
    max_level_score = 0

    for param, value in vitals_dict.items():
        if param not in VITAL_THRESHOLDS:
            continue
        result = _classify_value(param, value)
        result["parameter"] = param
        result["value"] = value
        analyses.append(result)

        # Tracking du niveau le plus grave
        weight = level_weights.get(result["level"], 0)
        if weight > max_level_score:
            max_level_score = weight

        # Génération des alertes
        if result["level"] in ("critical", "warning", "low"):
            alerts.append({
                "type": "vitals",
                "severity": "critical" if result["level"] == "critical" else "warning",
                "message": result["message"],
                "recommendation": result["recommendation"]
            })

    # Niveau global basé sur le paramètre le plus dégradé
    global_level_map = {0: "normal", 1: "low", 2: "warning", 3: "critical"}
    global_level = global_level_map.get(max_level_score, "normal")

    # Score normalisé 0-1
    score = round(max_level_score / 3, 2)

    return {
        "analyses": analyses,
        "global_level": global_level,
        "alerts": alerts,
        "score": score
    }