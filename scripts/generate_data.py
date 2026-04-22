"""
Script de génération des données synthétiques.
Encapsule la logique du notebook data_exploration.ipynb
pour l'intégrer dans le pipeline DVC.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import argparse

def generate_patient(patient_id: int, seed: int = 42) -> dict:
    age = random.randint(35, 85)
    has_hta = random.random() > 0.5
    has_diabetes = random.random() > 0.6
    has_cardiac = random.random() > 0.7
    base_systolic = 120 + (20 if has_hta else 0) + (age - 50) * 0.3
    base_glucose = 5.5 + (3.0 if has_diabetes else 0) + np.random.normal(0, 0.5)
    return {
        "patient_id": f"P{patient_id:04d}",
        "age": age,
        "gender": random.choice(["M", "F"]),
        "has_hta": has_hta,
        "has_diabetes": has_diabetes,
        "has_cardiac": has_cardiac,
        "base_systolic": round(base_systolic, 1),
        "base_glucose": round(base_glucose, 2),
        "n_comorbidities": sum([has_hta, has_diabetes, has_cardiac])
    }

def generate_vitals_history(patient: dict, n_days: int = 90) -> pd.DataFrame:
    records = []
    base_date = datetime(2024, 1, 1)
    for day in range(n_days):
        degradation = day * 0.05 * patient["n_comorbidities"]
        records.append({
            "patient_id": patient["patient_id"],
            "date": (base_date + timedelta(days=day)).strftime("%Y-%m-%d"),
            "day": day,
            "systolic_bp": round(patient["base_systolic"] + degradation + np.random.normal(0, 8), 1),
            "diastolic_bp": round(patient["base_systolic"] * 0.65 + np.random.normal(0, 5), 1),
            "heart_rate": round(72 + (10 if patient["has_cardiac"] else 0) + np.random.normal(0, 6), 1),
            "glucose": round(patient["base_glucose"] + np.random.normal(0, 0.8), 2),
            "weight": round(70 + patient["age"] * 0.1 + np.random.normal(0, 1.5), 1),
            "temperature": round(np.random.normal(37.0, 0.3), 1),
        })
    return pd.DataFrame(records)

CONSULTATION_TEMPLATES = {
    "cardio": [
        "Patient se plaint de douleurs thoraciques depuis {n} jours. Légère dyspnée à l'effort.",
        "Consultation pour palpitations récurrentes. Tachycardie à {hr} bpm.",
    ],
    "metabolic": [
        "Contrôle diabète type 2. Glycémie à jeun à {gl} mmol/L.",
        "Patient en surpoids. Fatigue chronique, soif excessive.",
    ],
    "infectious": [
        "Fièvre à {temp}°C depuis {n} jours. Toux productive.",
        "Infection urinaire suspectée. Brûlures mictionnelles.",
    ],
    "normal": [
        "Consultation de routine. Pas de plainte particulière.",
        "Renouvellement d'ordonnance. Patient asymptomatique.",
    ]
}

def generate_consultation_note(patient: dict) -> dict:
    if patient["has_cardiac"] and random.random() > 0.4:
        category = "cardio"
    elif patient["has_diabetes"] and random.random() > 0.4:
        category = "metabolic"
    elif random.random() > 0.7:
        category = "infectious"
    else:
        category = "normal"
    template = random.choice(CONSULTATION_TEMPLATES[category])
    note = template.format(
        n=random.randint(2, 14), hr=random.randint(95, 130),
        gl=round(patient["base_glucose"] + random.uniform(-1, 3), 1),
        temp=round(37.5 + random.uniform(0, 2), 1)
    )
    return {
        "patient_id": patient["patient_id"],
        "note": note,
        "category": category,
        "label": 1 if category != "normal" else 0
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-patients", type=int, default=200)
    parser.add_argument("--n-notes", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="data/synthetic")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    # Génération patients
    patients = [generate_patient(i, args.seed) for i in range(1, args.n_patients + 1)]
    df_patients = pd.DataFrame(patients)
    df_patients.to_csv(f"{args.output_dir}/patients.csv", index=False)

    # Génération vitaux
    all_vitals = pd.concat(
        [generate_vitals_history(p) for p in patients[:20]], ignore_index=True
    )
    all_vitals.to_csv(f"{args.output_dir}/vitals_history.csv", index=False)

    # Génération notes
    notes = [generate_consultation_note(random.choice(patients)) for _ in range(args.n_notes)]
    df_notes = pd.DataFrame(notes)
    df_notes.to_csv(f"{args.output_dir}/consultation_notes.csv", index=False)

    print(f" Données générées dans {args.output_dir}/")
    print(f"  → {len(df_patients)} patients")
    print(f"  → {len(all_vitals)} mesures vitaux")
    print(f"  → {len(df_notes)} notes de consultation")

if __name__ == "__main__":
    main()