"""
Utilitaires d'authentification JWT.
Gestion des tokens, hachage de mots de passe, vérification des droits.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from utils.config import settings
from models.auth import TokenData, UserRole

# ─────────────────────────────────────────────────────
# Configuration du hachage de mots de passe
# pbkdf2_sha256 évite les incompatibilités passlib/bcrypt
# observées sur certaines versions de l'environnement local.
# ─────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Schéma OAuth2 : indique à FastAPI où chercher le token
# Le token doit être dans le header : Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ─────────────────────────────────────────────────────
# Base de données utilisateurs en mémoire
# (remplacée par PostgreSQL à l'étape 16)
# ─────────────────────────────────────────────────────
_users_db = {
    "dr_martin": {
        "id": "user-001",
        "username": "dr_martin",
        "email": "martin@mediwatch.fr",
        "full_name": "Dr. Sophie Martin",
        "hashed_password": pwd_context.hash("mediwatch2024"),
        "role": UserRole.DOCTOR,
        "is_active": True
    },
    "admin": {
        "id": "user-002",
        "username": "admin",
        "email": "admin@mediwatch.fr",
        "full_name": "Administrateur MediWatch",
        "hashed_password": pwd_context.hash("admin2024"),
        "role": UserRole.ADMIN,
        "is_active": True
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe correspond au hash stocké."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hache un mot de passe avec pbkdf2_sha256."""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[dict]:
    """Récupère un utilisateur par son username."""
    return _users_db.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authentifie un utilisateur.
    Retourne l'utilisateur si valide, None sinon.
    Ne jamais indiquer si c'est le username ou le password qui est faux
    (sécurité : évite l'énumération des utilisateurs).
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un JWT signé avec la clé secrète.
    
    Le token encode :
    - sub : username (subject)
    - role : rôle de l'utilisateur
    - exp : date d'expiration
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dépendance FastAPI : extrait et valide le token JWT.
    Utilisé comme dépendance dans les routes protégées :
        @router.get("/protected")
        async def route(user = Depends(get_current_user)):
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(
            username=username,
            role=payload.get("role")
        )
    except JWTError:
        raise credentials_exception

    user = get_user(token_data.username)
    if user is None or not user["is_active"]:
        raise credentials_exception
    return user


async def get_current_active_doctor(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dépendance : vérifie que l'utilisateur est un médecin actif.
    Utilisé pour protéger les routes médicales sensibles.
    """
    if current_user["role"] not in (UserRole.DOCTOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux médecins"
        )
    return current_user


def require_role(*roles: UserRole):
    """
    Factory de dépendance pour vérifier un rôle spécifique.
    Usage : @router.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles requis : {[r.value for r in roles]}"
            )
        return current_user
    return role_checker