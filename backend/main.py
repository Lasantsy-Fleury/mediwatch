from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from api.routes import consultation, patient, simulation, auth

from api.routes import consultation, patient, simulation
from utils.metrics import active_patients_gauge, model_loaded_gauge
from utils.database import get_all_patients

# ─────────────────────────────────────────────────────
# Initialisation FastAPI
# ─────────────────────────────────────────────────────
app = FastAPI(
    title="MediWatch API",
    description="Assistant clinique contextuel multimodal pour soins de ville",
    version="0.1.0"
)

# ─────────────────────────────────────────────────────
# Middleware CORS
# ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────
# Instrumentation Prometheus
# Expose automatiquement /metrics avec :
# - latence HTTP par endpoint
# - nb requêtes par status code
# - requêtes en cours
# ─────────────────────────────────────────────────────
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health"],
    inprogress_name="mediwatch_http_requests_inprogress",
    inprogress_labels=True,
).instrument(app).expose(app)

# ─────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────
app.include_router(auth.router,         prefix="/api/v1", tags=["Authentification"])
app.include_router(consultation.router, prefix="/api/v1", tags=["Consultation"])
app.include_router(patient.router,      prefix="/api/v1", tags=["Patient"])
app.include_router(simulation.router,   prefix="/api/v1", tags=["Simulation"])


# ─────────────────────────────────────────────────────
# Événements de démarrage / arrêt
# ─────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Initialise la base de données et les métriques au démarrage."""
    from db.session import engine, Base, SessionLocal
    from db.models import PatientDB, ConsultationDB, UserDB
    from db.crud import seed_demo_patients

    # Création des tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    print(" Tables PostgreSQL créées")

    # Injection des données de démo
    db = SessionLocal()
    try:
        seed_demo_patients(db)
    finally:
        db.close()

    # Métriques Prometheus
    patients = get_all_patients()
    active_patients_gauge.set(len(patients))

    # Le modèle texte est chargé en lazy-loading dans le service.
    # Évite de bloquer le démarrage API si le modèle local est incomplet.
    model_loaded_gauge.labels(model_name="tfidf_logreg").set(0)

    print(" MediWatch API démarrée")


@app.on_event("shutdown")
async def shutdown_event():
    print(" MediWatch API arrêtée")


# ─────────────────────────────────────────────────────
# Routes de santé
# ─────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "message": "MediWatch API is running",
        "version": "0.1.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}