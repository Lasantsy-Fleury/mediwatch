"""
Configuration centralisée via variables d'environnement.
Utilise python-dotenv pour charger .env en développement.
En production (Render), les variables sont injectées directement.
"""
import os
from dotenv import load_dotenv

# Charge .env si présent (dev uniquement)
load_dotenv()


class Settings:
    """Configuration globale de l'application."""

    # Environnement
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # Base de données
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./mediwatch_dev.db"
    )

    # Chemins ML
    ML_MODELS_PATH: str = os.getenv("ML_MODELS_PATH", "ml_models")

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"


settings = Settings()