"""
Service NLP basé sur DistilBERT fine-tuné.
Remplace text_service.py pour les déploiements avec suffisamment de RAM.
Chargement lazy : le modèle n'est chargé qu'à la première requête.
"""
import torch
import numpy as np
import os
from typing import Optional

_distilbert_model = None
_distilbert_tokenizer = None
_distilbert_loaded = False

MODEL_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml_models", "text_distilbert", "best_model"
)
MAX_LEN = 128
DEVICE = torch.device("cpu")  # CPU pour la prod légère

LABEL_TO_CATEGORY = {0: "normal", 1: "cardio", 2: "metabolic", 3: "infectious"}

SUGGESTED_QUESTIONS = {
    "cardio": [
        "La douleur irradie-t-elle vers le bras gauche ou la mâchoire ?",
        "Avez-vous des antécédents familiaux de maladies cardiaques ?",
        "La douleur apparaît-elle à l'effort ou au repos ?"
    ],
    "metabolic": [
        "Avez-vous mesuré votre glycémie à jeun récemment ?",
        "Ressentez-vous une soif excessive ou une fatigue inhabituelle ?",
        "Vos traitements antidiabétiques sont-ils pris régulièrement ?"
    ],
    "infectious": [
        "Depuis combien de jours avez-vous de la fièvre ?",
        "Avez-vous été en contact avec des personnes malades ?",
        "Avez-vous des frissons ou des sueurs nocturnes ?"
    ],
    "neurological": [
        "Les céphalées sont-elles nouvelles ou récurrentes ?",
        "Avez-vous eu des troubles visuels associés ?"
    ]
}

SUGGESTED_EXAMS = {
    "cardio":    ["ECG", "Troponine", "BNP/NT-proBNP", "Échographie cardiaque"],
    "metabolic": ["Glycémie à jeun", "HbA1c", "Bilan lipidique", "TSH"],
    "infectious":["NFS", "CRP", "Hémocultures", "PCR grippe/COVID"],
    "normal":    []
}


def _load_distilbert():
    """Charge DistilBERT depuis le disque (lazy loading)."""
    global _distilbert_model, _distilbert_tokenizer, _distilbert_loaded

    if _distilbert_loaded:
        return True

    if not os.path.exists(MODEL_DIR):
        print(" Modèle DistilBERT introuvable — fallback text_service")
        return False

    try:
        from transformers import (
            DistilBertForSequenceClassification,
            DistilBertTokenizerFast
        )
        print(" Chargement DistilBERT (peut prendre 30s)...")
        _distilbert_tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
        _distilbert_model = DistilBertForSequenceClassification.from_pretrained(
            MODEL_DIR
        ).to(DEVICE)
        _distilbert_model.eval()
        _distilbert_loaded = True
        print(" DistilBERT fine-tuné chargé")
        return True
    except Exception as e:
        print(f" Erreur chargement DistilBERT : {e}")
        return False


def analyze_with_distilbert(note_text: str) -> dict:
    """
    Analyse une note médicale avec DistilBERT fine-tuné.
    Fallback automatique vers text_service si DistilBERT indisponible.
    """
    if not note_text or len(note_text.strip()) < 5:
        return {
            "risk_scores": [], "alerts": [],
            "suggested_questions": [], "suggested_exams": [],
            "summary": "Note trop courte.", "model_used": "none"
        }

    if not _load_distilbert():
        from services.text_service import analyze_consultation_text
        return analyze_consultation_text(note_text)

    encoding = _distilbert_tokenizer(
        note_text,
        truncation=True,
        max_length=MAX_LEN,
        padding="max_length",
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = _distilbert_model(
            input_ids=encoding["input_ids"].to(DEVICE),
            attention_mask=encoding["attention_mask"].to(DEVICE)
        )
        probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()

    pred_label = int(probs.argmax())
    pred_category = LABEL_TO_CATEGORY[pred_label]
    confidence = float(probs[pred_label])

    # Construction des scores de risque
    risk_scores = []
    for i, (label, cat) in enumerate(LABEL_TO_CATEGORY.items()):
        if cat == "normal":
            continue
        score = float(probs[i])
        if score < 0.05:
            continue
        level = "high" if score >= 0.7 else "medium" if score >= 0.35 else "low"
        risk_scores.append({
            "category": cat,
            "label": cat.capitalize(),
            "level": level,
            "score": round(score, 3),
            "explanation": f"DistilBERT — probabilité {round(score*100, 1)}%"
        })

    risk_scores.sort(key=lambda x: x["score"], reverse=True)

    alerts = []
    if pred_category != "normal" and confidence > 0.5:
        alerts.append({
            "type": pred_category,
            "severity": "critical" if confidence > 0.8 else "warning",
            "message": f"[DistilBERT] {pred_category.upper()} — confiance {round(confidence*100,1)}%",
            "recommendation": f"Bilans : {', '.join(SUGGESTED_EXAMS.get(pred_category, [])[:2])}"
        })

    return {
        "risk_scores": risk_scores,
        "alerts": alerts,
        "suggested_questions": SUGGESTED_QUESTIONS.get(pred_category, [])[:3],
        "suggested_exams": SUGGESTED_EXAMS.get(pred_category, [])[:4],
        "summary": (
            f"[DistilBERT] Catégorie : {pred_category.upper()} "
            f"(confiance {round(confidence*100,1)}%)"
        ),
        "model_used": "distilbert_finetuned",
        "predicted_category": pred_category,
        "confidence": round(confidence, 3)
    }