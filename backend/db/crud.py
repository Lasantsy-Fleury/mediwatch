"""
Opérations CRUD sur la base PostgreSQL.
Remplace les fonctions du fichier utils/database.py (store en mémoire).
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from db.models import PatientDB, ConsultationDB, UserDB, generate_uuid
from datetime import datetime


# ─────────────────────────────────────────────────────
# CRUD Patients
# ─────────────────────────────────────────────────────

def get_all_patients_db(db: Session) -> List[PatientDB]:
    return db.query(PatientDB).order_by(desc(PatientDB.created_at)).all()


def get_patient_by_id_db(db: Session, patient_id: str) -> Optional[PatientDB]:
    return db.query(PatientDB).filter(PatientDB.id == patient_id).first()


def create_patient_db(db: Session, patient_data: dict) -> PatientDB:
    patient = PatientDB(
        id=generate_uuid(),
        **patient_data
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient_risk_scores_db(
    db: Session, patient_id: str, risk_scores: list
) -> bool:
    patient = get_patient_by_id_db(db, patient_id)
    if not patient:
        return False
    patient.risk_scores = risk_scores
    db.commit()
    return True


def seed_demo_patients(db: Session) -> None:
    """Injecte les patients de démo si la base est vide."""
    if db.query(PatientDB).count() > 0:
        return

    demo_patients = [
        PatientDB(
            id="patient-001",
            first_name="Jean", last_name="Dupont",
            age=67, gender="M",
            comorbidities=[
                {"name": "Hypertension artérielle", "since": "2015", "severity": "modérée"},
                {"name": "Diabète type 2", "since": "2018", "severity": "légère"}
            ],
            current_medications=[
                {"name": "Amlodipine", "dosage": "5mg", "frequency": "1x/jour"},
                {"name": "Metformine", "dosage": "1000mg", "frequency": "2x/jour"}
            ]
        ),
        PatientDB(
            id="patient-002",
            first_name="Marie", last_name="Martin",
            age=45, gender="F",
            comorbidities=[{"name": "Asthme", "since": "2005", "severity": "légère"}],
            current_medications=[
                {"name": "Salbutamol", "dosage": "100µg", "frequency": "si besoin"}
            ]
        ),
        PatientDB(
            id="patient-003",
            first_name="Pierre", last_name="Bernard",
            age=72, gender="M",
            comorbidities=[
                {"name": "Insuffisance cardiaque", "since": "2020", "severity": "modérée"},
                {"name": "Fibrillation auriculaire", "since": "2021", "severity": "modérée"}
            ],
            current_medications=[
                {"name": "Bisoprolol", "dosage": "5mg", "frequency": "1x/jour"},
                {"name": "Furosémide", "dosage": "40mg", "frequency": "1x/jour"}
            ]
        )
    ]

    for p in demo_patients:
        db.add(p)
    db.commit()
    print(" Patients de démo injectés en base PostgreSQL")


# ─────────────────────────────────────────────────────
# CRUD Consultations
# ─────────────────────────────────────────────────────

def save_consultation_db(
    db: Session, patient_id: str, consultation_data: dict
) -> ConsultationDB:
    vitals = consultation_data.get("raw_vitals_analysis", {})
    analyses = vitals.get("analyses", []) if vitals else []

    def get_vital(param):
        for a in analyses:
            if a.get("parameter") == param:
                return a.get("value")
        return None

    consultation = ConsultationDB(
        id=consultation_data.get("consultation_id", generate_uuid()),
        patient_id=patient_id,
        note_text=consultation_data.get("note_text"),
        analysis_summary=consultation_data.get("summary"),
        risk_scores=consultation_data.get("risk_scores", []),
        alerts=consultation_data.get("alerts", []),
        suggested_questions=consultation_data.get("suggested_questions", []),
        suggested_exams=consultation_data.get("suggested_exams", []),
        raw_text_analysis=consultation_data.get("raw_text_analysis"),
        raw_vitals_analysis=consultation_data.get("raw_vitals_analysis"),
        raw_image_analysis=consultation_data.get("raw_image_analysis"),
        systolic_bp=get_vital("systolic_bp"),
        diastolic_bp=get_vital("diastolic_bp"),
        heart_rate=get_vital("heart_rate"),
        glucose=get_vital("glucose"),
        temperature=get_vital("temperature"),
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


def get_consultations_by_patient_db(
    db: Session, patient_id: str, limit: int = 50
) -> List[ConsultationDB]:
    return (
        db.query(ConsultationDB)
        .filter(ConsultationDB.patient_id == patient_id)
        .order_by(desc(ConsultationDB.created_at))
        .limit(limit)
        .all()
    )


def get_consultation_by_id_db(
    db: Session, consultation_id: str
) -> Optional[ConsultationDB]:
    return db.query(ConsultationDB).filter(
        ConsultationDB.id == consultation_id
    ).first()