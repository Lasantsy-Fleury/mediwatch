"""
Métriques Prometheus personnalisées pour MediWatch.
Ces métriques s'ajoutent aux métriques HTTP automatiques.
"""
try:
    from prometheus_client import Counter, Histogram, Gauge
except ImportError:
    class _NoOpMetric:
        def __init__(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

        def inc(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

    Counter = _NoOpMetric
    Histogram = _NoOpMetric
    Gauge = _NoOpMetric
import time

# ─────────────────────────────────────────────────────
# Compteurs — nombre d'événements cumulés
# ─────────────────────────────────────────────────────

consultations_total = Counter(
    "mediwatch_consultations_total",
    "Nombre total de consultations analysées",
    ["patient_id", "risk_level"]  # labels pour filtrer
)

alerts_generated_total = Counter(
    "mediwatch_alerts_total",
    "Nombre total d'alertes générées",
    ["alert_type", "severity"]
)

model_predictions_total = Counter(
    "mediwatch_model_predictions_total",
    "Nombre de prédictions ML effectuées",
    ["model_name", "predicted_category"]
)

# ─────────────────────────────────────────────────────
# Histogrammes — distribution des valeurs
# ─────────────────────────────────────────────────────

inference_duration_seconds = Histogram(
    "mediwatch_inference_duration_seconds",
    "Durée d'inférence ML par modalité",
    ["modality"],  # text, vitals, image, fusion
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

consultation_risk_score = Histogram(
    "mediwatch_consultation_risk_score",
    "Distribution des scores de risque des consultations",
    ["category"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# ─────────────────────────────────────────────────────
# Jauges — valeurs instantanées
# ─────────────────────────────────────────────────────

active_patients_gauge = Gauge(
    "mediwatch_active_patients",
    "Nombre de patients actifs dans le système"
)

model_loaded_gauge = Gauge(
    "mediwatch_model_loaded",
    "Indique si le modèle ML est chargé (1) ou non (0)",
    ["model_name"]
)


class InferenceTimer:
    """
    Context manager pour mesurer la durée d'inférence.
    Usage :
        with InferenceTimer("text"):
            result = analyze_text(note)
    """
    def __init__(self, modality: str):
        self.modality = modality
        self.start = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        duration = time.time() - self.start
        inference_duration_seconds.labels(
            modality=self.modality
        ).observe(duration)
