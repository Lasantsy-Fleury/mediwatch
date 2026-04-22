"""
Tests unitaires du service d'analyse des constantes vitales.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.timeseries_service import analyze_vitals
from models.consultation import VitalSigns


class TestAnalyzeVitals:
    """Tests du service d'analyse des constantes vitales."""

    def test_vitaux_normaux_niveau_normal(self):
        """Des constantes normales doivent retourner un niveau global normal."""
        vitals = VitalSigns(
            systolic_bp=118.0,
            diastolic_bp=76.0,
            heart_rate=70.0,
            glucose=5.5,
            temperature=36.8
        )
        result = analyze_vitals(vitals)
        assert result["global_level"] == "normal"
        assert result["score"] == 0.0

    def test_tension_critique_niveau_critical(self):
        """Une tension > 160 mmHg doit déclencher un niveau critique."""
        vitals = VitalSigns(systolic_bp=185.0)
        result = analyze_vitals(vitals)
        assert result["global_level"] == "critical"
        assert result["score"] == 1.0

    def test_tension_warning(self):
        """Une tension entre 130 et 160 doit déclencher un niveau warning."""
        vitals = VitalSigns(systolic_bp=145.0)
        result = analyze_vitals(vitals)
        assert result["global_level"] == "warning"

    def test_tachycardie_detectee(self):
        """Une FC > 100 bpm doit générer une alerte."""
        vitals = VitalSigns(heart_rate=125.0)
        result = analyze_vitals(vitals)
        assert len(result["alerts"]) > 0
        severities = [a["severity"] for a in result["alerts"]]
        assert "critical" in severities or "warning" in severities

    def test_hyperglycemie_critique(self):
        """Glycémie > 11.1 mmol/L doit être critique."""
        vitals = VitalSigns(glucose=14.0)
        result = analyze_vitals(vitals)
        analyses = {a["parameter"]: a for a in result["analyses"]}
        assert "glucose" in analyses
        assert analyses["glucose"]["level"] == "critical"

    def test_vitaux_vides_retourne_structure(self):
        """Des vitaux tous None ne doivent pas planter."""
        vitals = VitalSigns()
        result = analyze_vitals(vitals)
        assert isinstance(result, dict)
        assert "global_level" in result
        assert "analyses" in result
        assert "alerts" in result
        assert "score" in result

    def test_score_normalise(self):
        """Le score global doit être entre 0 et 1."""
        vitals = VitalSigns(systolic_bp=200.0, heart_rate=140.0, glucose=15.0)
        result = analyze_vitals(vitals)
        assert 0.0 <= result["score"] <= 1.0

    def test_structure_analyses_complete(self):
        """Chaque analyse doit avoir les champs requis."""
        vitals = VitalSigns(systolic_bp=145.0, heart_rate=95.0)
        result = analyze_vitals(vitals)
        required_keys = ["parameter", "value", "level", "message", "recommendation"]
        for analysis in result["analyses"]:
            for key in required_keys:
                assert key in analysis, f"Clé manquante dans analyse : {key}"