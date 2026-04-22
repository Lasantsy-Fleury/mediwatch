from typing import Dict, List, Optional
from datetime import datetime
import uuid

# ---------------------------------------------------------------------------
# Base de données en mémoire (in-memory store)
# Simule une vraie BDD le temps qu'on intègre PostgreSQL ou MongoDB plus tard.
# Toutes les données sont perdues au redémarrage du serveur — c'est normal.
# ---------------------------------------------------------------------------

# Structure : { patient_id: { ...données patient... } }
_patients_store: Dict[str, dict] = {}

# Structure : { consultation_id: { ...données consultation... } }
_consultations_store: Dict[str, dict] = {}

# Données de démonstration pré-chargées au démarrage
def _seed_demo_data():
    """Injecte 3 patients de démonstration avec historique."""
    demo_patients = [
        {
            "id": "patient-001",
            "first_name": "Jean",
            "last_name": "Dupont",
            "age": 67,
            "gender": "M",
            "comorbidities": [
                {"name": "Hypertension artérielle", "since": "2015", "severity": "modérée"},
                {"name": "Diabète type 2", "since": "2018", "severity": "légère"}
            ],
            "current_medications": [
                {"name": "Amlodipine", "dosage": "5mg", "frequency": "1x/jour"},
                {"name": "Metformine", "dosage": "1000mg", "frequency": "2x/jour"}
            ],
            "created_at": datetime(2024, 1, 15).isoformat(),
            "risk_scores": [],
            "consultations": []
        },
        {
            "id": "patient-002",
            "first_name": "Marie",
            "last_name": "Martin",
            "age": 45,
            "gender": "F",
            "comorbidities": [
                {"name": "Asthme", "since": "2005", "severity": "légère"}
            ],
            "current_medications": [
                {"name": "Salbutamol", "dosage": "100µg", "frequency": "si besoin"}
            ],
            "created_at": datetime(2024, 2, 10).isoformat(),
            "risk_scores": [],
            "consultations": []
        },
        {
            "id": "patient-003",
            "first_name": "Pierre",
            "last_name": "Bernard",
            "age": 72,
            "gender": "M",
            "comorbidities": [
                {"name": "Insuffisance cardiaque", "since": "2020", "severity": "modérée"},
                {"name": "Fibrillation auriculaire", "since": "2021", "severity": "modérée"},
                {"name": "Insuffisance rénale chronique", "since": "2019", "severity": "légère"}
            ],
            "current_medications": [
                {"name": "Bisoprolol", "dosage": "5mg", "frequency": "1x/jour"},
                {"name": "Furosémide", "dosage": "40mg", "frequency": "1x/jour"},
                {"name": "Apixaban", "dosage": "5mg", "frequency": "2x/jour"}
            ],
            "created_at": datetime(2023, 11, 5).isoformat(),
            "risk_scores": [],
            "consultations": []
        }
    ]

    for patient in demo_patients:
        _patients_store[patient["id"]] = patient


# Appel au démarrage du module
_seed_demo_data()


# ---------------------------------------------------------------------------
# Fonctions CRUD patients
# ---------------------------------------------------------------------------

def get_all_patients() -> List[dict]:
    return list(_patients_store.values())

def get_patient_by_id(patient_id: str) -> Optional[dict]:
    return _patients_store.get(patient_id)

def create_patient(patient_data: dict) -> dict:
    patient_id = str(uuid.uuid4())
    patient_data["id"] = patient_id
    patient_data["created_at"] = datetime.now().isoformat()
    patient_data["risk_scores"] = []
    patient_data["consultations"] = []
    _patients_store[patient_id] = patient_data
    return patient_data

def update_patient_risk_scores(patient_id: str, risk_scores: list) -> bool:
    if patient_id not in _patients_store:
        return False
    _patients_store[patient_id]["risk_scores"] = risk_scores
    return True


# ---------------------------------------------------------------------------
# Fonctions CRUD consultations
# ---------------------------------------------------------------------------

def get_consultations_by_patient(patient_id: str) -> List[dict]:
    return [
        c for c in _consultations_store.values()
        if c.get("patient_id") == patient_id
    ]

def save_consultation(consultation_data: dict) -> dict:
    consultation_id = consultation_data.get("consultation_id", str(uuid.uuid4()))
    consultation_data["consultation_id"] = consultation_id
    _consultations_store[consultation_id] = consultation_data

    # Référence dans la liste du patient
    patient_id = consultation_data.get("patient_id")
    if patient_id and patient_id in _patients_store:
        _patients_store[patient_id]["consultations"].append(consultation_id)

    return consultation_data

def get_consultation_by_id(consultation_id: str) -> Optional[dict]:
    return _consultations_store.get(consultation_id)