"""
Configuration globale des tests pytest.
Les fixtures définies ici sont disponibles dans tous les fichiers de test.
"""
import pytest
import sys
import os

# Ajoute le dossier backend au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def client():
    """
    Client de test FastAPI.
    Simule des requêtes HTTP sans démarrer un vrai serveur.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_vitals():
    """Constantes vitales de test."""
    return {
        "systolic_bp": 145.0,
        "diastolic_bp": 92.0,
        "heart_rate": 88.0,
        "glucose": 7.2,
        "temperature": 37.8
    }


@pytest.fixture
def sample_consultation_payload():
    """Payload de consultation complet pour les tests d'endpoints."""
    return {
        "patient_id": "patient-001",
        "note_text": "Patient avec douleur thoracique sévère et tachycardie.",
        "vitals": {
            "systolic_bp": 172.0,
            "diastolic_bp": 98.0,
            "heart_rate": 115.0,
            "glucose": 12.5
        }
    }


@pytest.fixture
def normal_consultation_payload():
    """Payload de consultation normale (pas de risque)."""
    return {
        "patient_id": "patient-002",
        "note_text": "Consultation de routine. Pas de plainte. Renouvellement ordonnance.",
        "vitals": {
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "heart_rate": 68.0,
            "temperature": 36.9
        }
    }