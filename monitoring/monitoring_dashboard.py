"""
Monitoring de drift des données avec Evidently AI.
Détecte si la distribution des features change au fil du temps
(ex: les patients soumis à l'API deviennent différents des données d'entraînement).
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    from evidently.metrics import (
        ColumnDriftMetric,
        DatasetDriftMetric,
        DatasetMissingValuesSummaryMetric
    )
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False
    print("⚠️ Evidently non installé — pip install evidently")


def generate_reference_data(n: int = 200) -> pd.DataFrame:
    """Données de référence : distribution d'entraînement."""
    np.random.seed(42)
    return pd.DataFrame({
        "systolic_bp":  np.random.normal(135, 20, n),
        "diastolic_bp": np.random.normal(85, 12, n),
        "heart_rate":   np.random.normal(78, 12, n),
        "glucose":      np.random.normal(6.5, 1.8, n),
        "age":          np.random.normal(58, 15, n),
        "note_length":  np.random.normal(120, 40, n),
    })


def generate_current_data(n: int = 100, drift: bool = False) -> pd.DataFrame:
    """
    Données courantes : simule ce que l'API reçoit en production.
    Si drift=True, simule un glissement de distribution (cas pathologique).
    """
    np.random.seed(99)
    if drift:
        # Simulation d'un drift : les patients sont en moyenne plus malades
        return pd.DataFrame({
            "systolic_bp":  np.random.normal(155, 25, n),  # Plus élevé
            "diastolic_bp": np.random.normal(95, 15, n),
            "heart_rate":   np.random.normal(90, 18, n),   # Plus élevé
            "glucose":      np.random.normal(9.0, 2.5, n), # Plus élevé
            "age":          np.random.normal(68, 12, n),   # Plus âgé
            "note_length":  np.random.normal(80, 30, n),   # Notes plus courtes
        })
    else:
        return pd.DataFrame({
            "systolic_bp":  np.random.normal(137, 21, n),
            "diastolic_bp": np.random.normal(86, 12, n),
            "heart_rate":   np.random.normal(79, 13, n),
            "glucose":      np.random.normal(6.7, 1.9, n),
            "age":          np.random.normal(59, 15, n),
            "note_length":  np.random.normal(118, 42, n),
        })


def run_drift_analysis(output_dir: str = "monitoring") -> dict:
    """Lance l'analyse de drift et génère le rapport HTML."""
    os.makedirs(output_dir, exist_ok=True)

    reference_data = generate_reference_data(200)
    current_data = generate_current_data(100, drift=False)

    if not EVIDENTLY_AVAILABLE:
        # Fallback manuel si Evidently absent
        drift_results = {}
        for col in reference_data.columns:
            ref_mean = reference_data[col].mean()
            cur_mean = current_data[col].mean()
            drift_pct = abs(cur_mean - ref_mean) / (ref_mean + 1e-9) * 100
            drift_results[col] = {
                "reference_mean": round(ref_mean, 2),
                "current_mean": round(cur_mean, 2),
                "drift_percent": round(drift_pct, 2),
                "drifted": drift_pct > 10
            }

        report = {
            "generated_at": datetime.now().isoformat(),
            "n_reference": len(reference_data),
            "n_current": len(current_data),
            "drift_results": drift_results,
            "n_drifted_features": sum(1 for v in drift_results.values() if v["drifted"])
        }

        with open(f"{output_dir}/drift_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f" Rapport de drift (fallback) sauvegardé")
        print(f"Features en drift : {report['n_drifted_features']}/{len(drift_results)}")
        return report

    # Rapport Evidently complet
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset(),
        DatasetMissingValuesSummaryMetric(),
    ])
    report.run(
        reference_data=reference_data,
        current_data=current_data
    )

    # Sauvegarde HTML
    html_path = f"{output_dir}/drift_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
    report.save_html(html_path)

    # Sauvegarde JSON des métriques
    report_dict = report.as_dict()
    with open(f"{output_dir}/drift_metrics.json", "w") as f:
        json.dump(report_dict, f, indent=2, default=str)

    print(f" Rapport Evidently sauvegardé : {html_path}")
    return report_dict


if __name__ == "__main__":
    run_drift_analysis()