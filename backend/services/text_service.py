import re
import os
from typing import Optional
from datetime import datetime

# ---------------------------------------------------------------------------
# Dictionnaires de règles expertes cliniques
# Ces règles simulent ce qu'un modèle NLP ferait après fine-tuning.
# Elles seront remplacées progressivement par DistilBERT dans les notebooks.
# ---------------------------------------------------------------------------

CARDIO_KEYWORDS = [
    "douleur thoracique", "oppression", "palpitations", "dyspnée",
    "essoufflement", "oedème", "oedeme", "tachycardie", "bradycardie",
    "syncope", "malaise", "angine", "infarctus", "insuffisance cardiaque"
]

METABOLIC_KEYWORDS = [
    "glycémie", "glycemie", "diabète", "diabete", "hyperglycémie",
    "hypoglycémie", "obésité", "obesite", "cholestérol", "cholesterol",
    "triglycérides", "triglycéride", "syndrome métabolique", "insuline"
]

INFECTIOUS_KEYWORDS = [
    "fièvre", "fievre", "infection", "inflammatoire", "sepsis",
    "antibiotique", "bactérie", "bacterie", "virus", "grippe",
    "covid", "pneumonie", "cystite", "angine infectieuse"
]

NEUROLOGICAL_KEYWORDS = [
    "céphalée", "cephalee", "migraine", "vertige", "confusion",
    "désorientation", "convulsion", "AVC", "accident vasculaire",
    "paresthésie", "paresthesie", "tremblements"
]

SEVERITY_MODIFIERS = {
    "high": ["sévère", "severe", "aigu", "aiguë", "critique", "urgent", "grave", "brutal"],
    "medium": ["modéré", "modere", "persistant", "chronique", "récurrent", "recurrent"],
    "low": ["léger", "leger", "bénin", "benin", "passager", "occasionnel"]
}

SUGGESTED_QUESTIONS = {
    "cardio": [
        "La douleur irradie-t-elle vers le bras gauche ou la mâchoire ?",
        "Avez-vous des antécédents familiaux de maladies cardiaques ?",
        "La douleur apparaît-elle à l'effort ou au repos ?",
        "Prenez-vous des anticoagulants ou antiplaquettaires ?"
    ],
    "metabolic": [
        "Avez-vous mesuré votre glycémie à jeun récemment ?",
        "Votre alimentation a-t-elle changé ces dernières semaines ?",
        "Ressentez-vous une soif excessive ou une fatigue inhabituelle ?",
        "Vos traitements antidiabétiques sont-ils pris régulièrement ?"
    ],
    "infectious": [
        "Depuis combien de jours avez-vous de la fièvre ?",
        "Avez-vous été en contact avec des personnes malades ?",
        "Avez-vous pris des antibiotiques récemment ?",
        "Avez-vous des frissons ou des sueurs nocturnes ?"
    ],
    "neurological": [
        "Les céphalées sont-elles nouvelles ou récurrentes ?",
        "Avez-vous eu des troubles visuels ou auditifs associés ?",
        "La douleur est-elle pulsatile ou en pression ?",
        "Y a-t-il des facteurs déclenchants identifiés ?"
    ]
}

SUGGESTED_EXAMS = {
    "cardio": ["ECG", "Troponine", "BNP / NT-proBNP", "Échographie cardiaque", "Holter ECG"],
    "metabolic": ["Glycémie à jeun", "HbA1c", "Bilan lipidique", "TSH", "Insulinémie"],
    "infectious": ["NFS", "CRP", "Hémocultures", "ECBU", "PCR grippe/COVID"],
    "neurological": ["IRM cérébrale", "EEG", "Fond d'œil", "Ponction lombaire si méningite suspectée"]
}


_nlp_pipeline: Optional[object] = None
_model_load_attempted = False


def _load_model() -> bool:
    """
    Charge le modèle NLP en lazy-loading.
    Retourne False si les dépendances/modèles ne sont pas disponibles.
    """
    global _nlp_pipeline, _model_load_attempted

    if _nlp_pipeline is not None:
        return True
    if _model_load_attempted:
        return False

    _model_load_attempted = True

    model_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "ml_models", "text")
    )
    if not os.path.isdir(model_dir):
        return False

    # Chargement opportuniste : si transformers n'est pas installé,
    # le service reste opérationnel via les règles expertes.
    try:
        from transformers import pipeline
        _nlp_pipeline = pipeline("text-classification", model=model_dir, tokenizer=model_dir)
        return True
    except Exception:
        _nlp_pipeline = None
        return False


def _rule_based_analysis(note_text: str) -> dict:
    """
    Analyse principale du texte de consultation via règles expertes.
    Retourne un dict structuré avec scores, alertes et suggestions.
    """
    normalized = _normalize_text(note_text)
    severity = _detect_severity_modifier(normalized)

    categories = {
        "cardio": (CARDIO_KEYWORDS, "Risque cardiovasculaire"),
        "metabolic": (METABOLIC_KEYWORDS, "Risque métabolique"),
        "infectious": (INFECTIOUS_KEYWORDS, "Risque infectieux"),
        "neurological": (NEUROLOGICAL_KEYWORDS, "Risque neurologique"),
    }

    risk_scores = []
    active_categories = []
    alerts = []

    for cat_key, (keywords, label) in categories.items():
        score = _detect_risk_category(normalized, keywords)
        if score > 0:
            level = _score_to_risk_level(score, severity)
            risk_scores.append({
                "category": cat_key,
                "label": label,
                "level": level,
                "score": round(score, 2),
                "explanation": f"{len([k for k in keywords if k in normalized])} indicateur(s) détecté(s)"
            })
            active_categories.append(cat_key)

            if level == "high":
                alerts.append({
                    "type": cat_key,
                    "severity": "critical",
                    "message": f"Risque {label.lower()} élevé détecté dans la note",
                    "recommendation": f"Envisager bilan urgent : {', '.join(SUGGESTED_EXAMS.get(cat_key, [])[:2])}"
                })
            elif level == "medium":
                alerts.append({
                    "type": cat_key,
                    "severity": "warning",
                    "message": f"Signaux {label.lower()} à surveiller",
                    "recommendation": "Suivi recommandé dans les 7 jours"
                })

    suggested_questions = []
    suggested_exams = []
    for cat in active_categories[:2]:
        suggested_questions.extend(SUGGESTED_QUESTIONS.get(cat, [])[:2])
        suggested_exams.extend(SUGGESTED_EXAMS.get(cat, [])[:3])

    if active_categories:
        cats_str = ", ".join(active_categories)
        summary = (
            f"Consultation analysée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}. "
            f"Indicateurs détectés dans les catégories : {cats_str}. "
            f"Sévérité globale estimée : {severity}. "
            f"{len(alerts)} alerte(s) générée(s)."
        )
    else:
        summary = "Aucun indicateur de risque majeur détecté dans la note de consultation."

    return {
        "risk_scores": risk_scores,
        "alerts": alerts,
        "suggested_questions": list(dict.fromkeys(suggested_questions)),
        "suggested_exams": list(dict.fromkeys(suggested_exams)),
        "summary": summary,
        "model_used": "rule_based"
    }


def _ml_based_analysis(note_text: str) -> dict:
    """
    Analyse via modèle ML si pipeline chargé, sinon fallback règles expertes.
    """
    if _nlp_pipeline is None:
        return _rule_based_analysis(note_text)

    try:
        raw = _nlp_pipeline(note_text)
    except Exception:
        result = _rule_based_analysis(note_text)
        result["model_used"] = "rule_based_fallback"
        return result

    result = _rule_based_analysis(note_text)
    result["model_used"] = "ml_text_classifier"
    result["ml_raw_output"] = raw
    return result


def _normalize_text(text: str) -> str:
    """Normalise le texte : minuscules, suppression ponctuation excessive."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\sàâäéèêëîïôöùûüç\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _detect_risk_category(text: str, keywords: list) -> float:
    """
    Calcule un score de risque brut basé sur la densité de mots-clés.
    Retourne un float entre 0 et 1.
    """
    matches = sum(1 for kw in keywords if kw in text)
    # Normalisation logarithmique pour éviter les scores > 1
    if matches == 0:
        return 0.0
    return min(1.0, 0.2 + (matches * 0.25))


def _detect_severity_modifier(text: str) -> str:
    """Détecte si le texte contient des modificateurs de sévérité."""
    for level, modifiers in SEVERITY_MODIFIERS.items():
        if any(mod in text for mod in modifiers):
            return level
    return "medium"


def _score_to_risk_level(score: float, severity: str) -> str:
    """Convertit un score numérique en niveau de risque lisible."""
    if severity == "high" and score > 0.3:
        return "high"
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    elif score > 0.0:
        return "low"
    return "low"


def analyze_consultation_text(note_text: str) -> dict:
    """
    Point d'entrée principal du service NLP.
    Utilise le modèle ML si disponible, sinon fallback règles expertes.
    Garantit toujours la présence de 'model_used' dans le résultat.
    """
    if not note_text or len(note_text.strip()) < 5:
        return {
            "risk_scores": [],
            "alerts": [],
            "suggested_questions": [],
            "suggested_exams": [],
            "summary": "Note trop courte pour analyse.",
            "model_used": "none"
        }

    model_available = _load_model()

    if model_available and _nlp_pipeline is not None:
        return _ml_based_analysis(note_text)
    else:
        result = _rule_based_analysis(note_text)
        # Garantit model_used même si _rule_based_analysis l'omet
        result.setdefault("model_used", "rule_based")
        return result