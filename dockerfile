# ─────────────────────────────────────────────
# Étape 1 : image de base Python légère
# On utilise slim pour réduire la taille finale
# ─────────────────────────────────────────────
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="MediWatch"
LABEL version="0.1.0"
LABEL description="Assistant clinique multimodal — Backend FastAPI"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Répertoire de travail dans le conteneur
WORKDIR /app

# ─────────────────────────────────────────────
# Étape 2 : installation des dépendances système
# Nécessaires pour Pillow et OpenCV
# ─────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────
# Étape 3 : installation des dépendances Python
# On copie d'abord requirements.txt seul pour
# profiter du cache Docker (si le code change
# mais pas les deps, cette couche est réutilisée)
# ─────────────────────────────────────────────
COPY requirements_prod.txt .
RUN pip install --no-cache-dir -r requirements_prod.txt

# ─────────────────────────────────────────────
# Étape 4 : copie du code source
# ─────────────────────────────────────────────
COPY backend/ ./backend/
COPY ml_models/ ./ml_models/

# ─────────────────────────────────────────────
# Étape 5 : exposition du port et démarrage
# ─────────────────────────────────────────────
EXPOSE 8000

# Utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Commande de démarrage
CMD ["uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2"]