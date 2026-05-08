"""
Configuration de la session SQLAlchemy.
Gère la connexion à PostgreSQL et fournit les sessions de base de données.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# URL de connexion — fallback SQLite pour les tests locaux sans Docker
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://mediwatch:mediwatch2024@localhost:5432/mediwatch_db"
)

# Pour les tests : utilise SQLite en mémoire
TESTING = os.getenv("TESTING", "false").lower() == "true"
if TESTING:
    DATABASE_URL = "sqlite:///./test.db"

# SQLite ne supporte pas pool_size/max_overflow, donc on gère ce cas a part.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,          # Connexions simultanées max
            max_overflow=10,      # Connexions supplémentaires autorisées
            pool_pre_ping=True,   # Vérifie la connexion avant utilisation
            echo=False            # True pour debugger les requêtes SQL
        )
        # Validate connectivity early to avoid opaque startup crashes.
        with engine.connect():
            pass
    except Exception as exc:
        print(f"[DB] PostgreSQL indisponible ({exc}). Fallback SQLite active.")
        DATABASE_URL = "sqlite:///./mediwatch_local.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI pour injecter une session DB dans les routes.
    Garantit que la session est fermée après chaque requête.
    
    Usage dans une route :
        @router.get("/patients")
        async def list_patients(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()