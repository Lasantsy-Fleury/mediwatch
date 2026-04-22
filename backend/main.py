from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import des routers (on les remplira dans les prochaines étapes)
from api.routes import consultation, patient, simulation

# ----------------------------
# Initialisation de l'application FastAPI
# ----------------------------
app = FastAPI(
    title="MediWatch API",
    description="Assistant clinique contextuel multimodal pour soins de ville",
    version="0.1.0"
)

# ----------------------------
# Configuration CORS
# Permet au frontend React (localhost:5173) de communiquer avec le backend
# Sans ça, le navigateur bloquera toutes les requêtes cross-origin
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL du frontend Vite par défaut
    allow_credentials=True,
    allow_methods=["*"],   # Autorise GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],   # Autorise tous les headers HTTP
)

# ----------------------------
# Inclusion des routers
# Chaque router gère un groupe de endpoints liés à une fonctionnalité
# ----------------------------
app.include_router(
    consultation.router,
    prefix="/api/v1",
    tags=["Consultation"]
)
app.include_router(
    patient.router,
    prefix="/api/v1",
    tags=["Patient"]
)
app.include_router(
    simulation.router,
    prefix="/api/v1",
    tags=["Simulation"]
)

# ----------------------------
# Route de santé (health check)
# Permet de vérifier rapidement que le serveur tourne
# ----------------------------
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