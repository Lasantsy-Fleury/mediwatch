import base64
import io
from typing import Optional

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ---------------------------------------------------------------------------
# Classificateur de lésions basé sur des règles colorimétriques simples.
# Version de base — sera remplacée par MobileNetV2 dans les notebooks ML.
# ---------------------------------------------------------------------------

LESION_CATEGORIES = {
    "erythema": {
        "label": "Érythème / Rougeur",
        "description": "Zone de rougeur cutanée",
        "risk_level": "low",
        "recommendations": ["Observer l'évolution sur 48h", "Écarter une réaction allergique"]
    },
    "hyperpigmentation": {
        "label": "Hyperpigmentation",
        "description": "Zone de peau plus sombre",
        "risk_level": "low",
        "recommendations": ["Surveiller la croissance", "Consulter dermatologue si évolution"]
    },
    "wound": {
        "label": "Plaie / Lésion ouverte",
        "description": "Discontinuité cutanée détectée",
        "risk_level": "medium",
        "recommendations": ["Évaluer la profondeur", "Nettoyage antiseptique", "Vérifier statut vaccinal tétanos"]
    },
    "edema": {
        "label": "Œdème",
        "description": "Gonflement cutané détecté",
        "risk_level": "medium",
        "recommendations": ["Rechercher une insuffisance veineuse", "Bilan rénal si bilatéral"]
    },
    "normal": {
        "label": "Aspect normal",
        "description": "Aucune anomalie détectée",
        "risk_level": "low",
        "recommendations": []
    }
}


def _decode_base64_image(image_base64: str) -> Optional[object]:
    """Décode une image base64 en objet PIL Image."""
    if not PIL_AVAILABLE:
        return None
    try:
        # Supprime le header data:image/...;base64, si présent
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return image
    except Exception:
        return None


def _analyze_color_profile(image) -> dict:
    """
    Analyse colorimétrique simple pour classifier la lésion.
    Calcule les canaux RGB moyens et détecte des patterns de base.
    Cette fonction sera remplacée par CNN dans les notebooks.
    """
    if not PIL_AVAILABLE or image is None:
        return {"category": "normal", "confidence": 0.5}

    import numpy as np

    # Redimensionner pour accélérer le traitement
    image_resized = image.resize((224, 224))
    img_array = np.array(image_resized, dtype=np.float32) / 255.0

    r_mean = float(img_array[:, :, 0].mean())
    g_mean = float(img_array[:, :, 1].mean())
    b_mean = float(img_array[:, :, 2].mean())

    # Règles colorimétriques simples
    # Rouge dominant → érythème potentiel
    if r_mean > 0.55 and r_mean > g_mean + 0.1 and r_mean > b_mean + 0.1:
        return {"category": "erythema", "confidence": 0.65}

    # Zone très sombre → hyperpigmentation potentielle
    if r_mean < 0.35 and g_mean < 0.35 and b_mean < 0.35:
        return {"category": "hyperpigmentation", "confidence": 0.60}

    # Fort contraste local → plaie potentielle
    std = float(img_array.std())
    if std > 0.25:
        return {"category": "wound", "confidence": 0.55}

    # Teinte rosée uniforme → œdème possible
    if abs(r_mean - g_mean) < 0.05 and r_mean > 0.55:
        return {"category": "edema", "confidence": 0.50}

    return {"category": "normal", "confidence": 0.70}


def analyze_image(image_base64: str, description: Optional[str] = None) -> dict:
    """
    Analyse principale d'une image de lésion.
    
    Args:
        image_base64: Image encodée en base64
        description: Description textuelle optionnelle du médecin
        
    Returns:
        dict avec keys: category, label, risk_level, confidence, recommendations, alerts
    """
    if not image_base64:
        return {
            "category": "no_image",
            "label": "Pas d'image fournie",
            "risk_level": "low",
            "confidence": 1.0,
            "recommendations": [],
            "alerts": []
        }

    image = _decode_base64_image(image_base64)

    if image is None:
        return {
            "category": "error",
            "label": "Image non décodable",
            "risk_level": "low",
            "confidence": 0.0,
            "recommendations": ["Vérifier le format de l'image (JPG, PNG)"],
            "alerts": []
        }

    # Analyse colorimétrique
    color_result = _analyze_color_profile(image)
    category = color_result["category"]
    confidence = color_result["confidence"]

    # Enrichissement par description textuelle
    if description:
        desc_lower = description.lower()
        if any(w in desc_lower for w in ["plaie", "coupure", "saigne", "ouvert"]):
            category = "wound"
            confidence = max(confidence, 0.75)
        elif any(w in desc_lower for w in ["gonfl", "oedème", "oedeme"]):
            category = "edema"
            confidence = max(confidence, 0.70)
        elif any(w in desc_lower for w in ["rouge", "érythème", "erytheme"]):
            category = "erythema"
            confidence = max(confidence, 0.70)

    cat_info = LESION_CATEGORIES.get(category, LESION_CATEGORIES["normal"])

    # Génération alertes si risque médium ou plus
    alerts = []
    if cat_info["risk_level"] in ("medium", "high"):
        alerts.append({
            "type": "image",
            "severity": "warning",
            "message": f"Lésion détectée : {cat_info['label']}",
            "recommendation": cat_info["recommendations"][0] if cat_info["recommendations"] else ""
        })

    return {
        "category": category,
        "label": cat_info["label"],
        "description": cat_info["description"],
        "risk_level": cat_info["risk_level"],
        "confidence": round(confidence, 2),
        "recommendations": cat_info["recommendations"],
        "alerts": alerts
    }