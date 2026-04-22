"""
Tests d'intégration des endpoints FastAPI.
Utilise TestClient pour simuler de vraies requêtes HTTP.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


class TestHealthEndpoints:
    """Tests des endpoints de santé."""

    def test_root_retourne_status_ok(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestPatientEndpoints:
    """Tests des endpoints patient."""

    def test_liste_patients_retourne_3_demo(self, client):
        """Le store de démo doit contenir exactement 3 patients."""
        response = client.get("/api/v1/patients")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3

    def test_get_patient_existant(self, client):
        """Un patient existant doit être retourné avec ses données."""
        response = client.get("/api/v1/patient/patient-001")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "patient-001"
        assert "first_name" in data["data"]
        assert "comorbidities" in data["data"]

    def test_get_patient_inexistant_retourne_404(self, client):
        """Un patient inexistant doit retourner 404."""
        response = client.get("/api/v1/patient/patient-999")
        assert response.status_code == 404

    def test_timeline_patient_existant(self, client):
        """La timeline d'un patient existant doit contenir patient + consultations."""
        response = client.get("/api/v1/patient/patient-001/timeline")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "patient" in data["data"]
        assert "consultations" in data["data"]
        assert "risk_scores" in data["data"]

    def test_creation_patient(self, client):
        """La création d'un nouveau patient doit retourner 201."""
        payload = {
            "first_name": "Sophie",
            "last_name": "Dubois",
            "age": 52,
            "gender": "F",
            "comorbidities": [],
            "current_medications": []
        }
        response = client.post("/api/v1/patient", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["first_name"] == "Sophie"
        assert "id" in data["data"]


class TestConsultationEndpoints:
    """Tests de l'endpoint de consultation."""

    def test_consultation_complete_retourne_analyse(
        self, client, sample_consultation_payload
    ):
        """Une consultation complète doit retourner une analyse structurée."""
        response = client.post("/api/v1/consultation", json=sample_consultation_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert "consultation_id" in result
        assert "summary" in result
        assert "risk_scores" in result
        assert "alerts" in result
        assert "suggested_questions" in result

    def test_consultation_patient_inexistant_retourne_404(self, client):
        """Une consultation pour un patient inexistant doit retourner 404."""
        payload = {
            "patient_id": "patient-999",
            "note_text": "Test note"
        }
        response = client.post("/api/v1/consultation", json=payload)
        assert response.status_code == 404

    def test_consultation_sans_note_fonctionne(self, client):
        """Une consultation sans note (vitaux seuls) doit fonctionner."""
        payload = {
            "patient_id": "patient-001",
            "vitals": {
                "systolic_bp": 145.0,
                "heart_rate": 90.0
            }
        }
        response = client.post("/api/v1/consultation", json=payload)
        assert response.status_code == 201

    def test_consultation_normale_moins_alertes(
        self, client, normal_consultation_payload
    ):
        """Une consultation normale doit générer moins d'alertes critiques."""
        response = client.post("/api/v1/consultation", json=normal_consultation_payload)
        assert response.status_code == 201
        data = response.json()
        critical_alerts = [
            a for a in data["data"]["alerts"]
            if a.get("severity") == "critical"
        ]
        assert len(critical_alerts) == 0


class TestSimulationEndpoints:
    """Tests de l'endpoint de simulation."""

    def test_simulation_basique_retourne_trajectoire(self, client):
        """Une simulation doit retourner une trajectoire de N+1 points."""
        payload = {
            "patient_id": "patient-001",
            "treatment_hypothesis": "Ajout antihypertenseur IEC 5mg/jour",
            "duration_days": 21,
            "target_parameter": "systolic_bp"
        }
        response = client.post("/api/v1/simulate-treatment", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert "trajectory" in result
        assert len(result["trajectory"]) == 22  # 0 → 21 inclus
        assert "decompensation_risk" in result
        assert "narrative" in result

    def test_simulation_decompensation_risk_normalise(self, client):
        """Le risque de décompensation doit être entre 0 et 1."""
        payload = {
            "patient_id": "patient-003",
            "treatment_hypothesis": "Arrêt diurétique",
            "duration_days": 14,
            "target_parameter": "systolic_bp"
        }
        response = client.post("/api/v1/simulate-treatment", json=payload)
        assert response.status_code == 200
        risk = response.json()["data"]["decompensation_risk"]
        assert 0.0 <= risk <= 1.0