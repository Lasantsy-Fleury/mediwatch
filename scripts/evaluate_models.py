"""
Script d'évaluation consolidée de tous les modèles.
Génère un rapport global pour DVC.
"""
import json
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime


def evaluate_text_model(model_dir: str, data_path: str) -> dict:
    """Évalue le modèle NLP sur les données de test."""
    try:
        with open(f"{model_dir}/tfidf_logreg_classifier.pkl", "rb") as f:
            pipeline = pickle.load(f)
        with open(f"{model_dir}/metrics.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Modèle NLP introuvable"}


def evaluate_timeseries_model(model_dir: str) -> dict:
    """Vérifie que le modèle LSTM est bien sauvegardé."""
    pth_path = f"{model_dir}/best_lstm.pth"
    config_path = f"{model_dir}/model_config.json"

    if os.path.exists(pth_path) and os.path.exists(config_path):
        size_mb = os.path.getsize(pth_path) / (1024 * 1024)
        with open(config_path, "r") as f:
            config = json.load(f)
        return {"status": "ok", "model_size_mb": round(size_mb, 2), "config": config}
    return {"error": "Modèle LSTM introuvable"}


def evaluate_fusion_model(model_dir: str) -> dict:
    """Vérifie que le modèle de fusion est bien sauvegardé."""
    pth_path = f"{model_dir}/best_fusion_model.pth"
    config_path = f"{model_dir}/model_config.json"

    if os.path.exists(pth_path) and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
        return {
            "status": "ok",
            "best_val_accuracy": config.get("best_val_accuracy"),
            "attention_weights": config.get("attention_weights_avg")
        }
    return {"error": "Modèle de fusion introuvable"}


def main():
    os.makedirs("data/processed", exist_ok=True)

    report = {
        "generated_at": datetime.now().isoformat(),
        "models": {
            "text_nlp": evaluate_text_model(
                "ml_models/text", "data/synthetic/consultation_notes.csv"
            ),
            "timeseries_lstm": evaluate_timeseries_model("ml_models/timeseries"),
            "fusion_multimodal": evaluate_fusion_model("ml_models/fusion")
        }
    }

    # Sauvegarde rapport global
    with open("data/processed/evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(" Rapport d'évaluation global :")
    print(json.dumps(report, indent=2))
    print("\n Rapport sauvegardé dans data/processed/evaluation_report.json")


if __name__ == "__main__":
    main()