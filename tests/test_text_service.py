"""
Tests unitaires du service NLP (text_service.py).
On teste les 2 modes : règles expertes et modèle ML.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.text_service import analyze_consultation_text


class TestAnalyzeConsultationText:
    """Tests du point d'entrée principal du service texte."""

    def test_note_vide_retourne_structure_vide(self):
        """Une note vide ne doit pas planter mais retourner une structure vide."""
        result = analyze_consultation_text("")
        assert isinstance(result, dict)
        assert "risk_scores" in result
        assert "alerts" in result
        assert "summary" in result
        assert len(result["risk_scores"]) == 0

    def test_note_trop_courte(self):
        """Une note de moins de 5 caractères retourne une réponse minimale."""
        result = analyze_consultation_text("ok")
        assert result["summary"] == "Note trop courte pour analyse."

    def test_note_cardio_detecte_risque(self):
        """Une note avec mots-clés cardio doit générer un score cardio."""
        note = "Patient avec douleur thoracique sévère et palpitations intenses."
        result = analyze_consultation_text(note)
        assert isinstance(result["risk_scores"], list)
        assert len(result["risk_scores"]) > 0
        categories = [r["category"] for r in result["risk_scores"]]
        assert "cardio" in categories

    def test_note_metabolique_detecte_risque(self):
        """Une note avec mots-clés métaboliques doit générer un score metabolic."""
        note = "Glycémie à 14 mmol/L. Patient diabétique sous insuline."
        result = analyze_consultation_text(note)
        categories = [r["category"] for r in result["risk_scores"]]
        assert "metabolic" in categories

    def test_note_infectieuse_detecte_risque(self):
        """Une note avec fièvre doit générer un score infectieux."""
        note = "Fièvre à 39.8°C depuis 3 jours. Toux productive. Frissons."
        result = analyze_consultation_text(note)
        categories = [r["category"] for r in result["risk_scores"]]
        assert "infectious" in categories

    def test_structure_retour_complete(self):
        """Le résultat doit toujours contenir les clés attendues."""
        note = "Douleur thoracique aiguë avec essoufflement."
        result = analyze_consultation_text(note)
        required_keys = [
            "risk_scores", "alerts", "suggested_questions",
            "suggested_exams", "summary", "model_used"
        ]
        for key in required_keys:
            assert key in result, f"Clé manquante : {key}"

    def test_score_normalise_entre_0_et_1(self):
        """Tous les scores de risque doivent être entre 0 et 1."""
        note = "Douleur thoracique sévère, palpitations, oedème."
        result = analyze_consultation_text(note)
        for score in result["risk_scores"]:
            assert 0.0 <= score["score"] <= 1.0, \
                f"Score hors plage : {score['score']}"

    def test_niveau_risque_valide(self):
        """Les niveaux de risque doivent être dans les valeurs autorisées."""
        note = "Insuffisance cardiaque aiguë avec tachycardie critique."
        result = analyze_consultation_text(note)
        valid_levels = {"low", "medium", "high", "critical"}
        for score in result["risk_scores"]:
            assert score["level"] in valid_levels, \
                f"Niveau invalide : {score['level']}"

    def test_alertes_ont_champs_requis(self):
        """Chaque alerte doit avoir type, severity, message, recommendation."""
        note = "Douleur thoracique sévère urgente avec syncope."
        result = analyze_consultation_text(note)
        for alert in result["alerts"]:
            assert "type" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "recommendation" in alert