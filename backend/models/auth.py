from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    DOCTOR = "doctor"
    ADMIN = "admin"
    READONLY = "readonly"


class UserCreate(BaseModel):
    """Schéma de création d'un utilisateur."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Email du praticien")
    password: str = Field(..., min_length=8, description="Mot de passe (min 8 chars)")
    full_name: str = Field(..., description="Nom complet du médecin")
    role: UserRole = Field(default=UserRole.DOCTOR)


class UserRead(BaseModel):
    """Schéma de lecture d'un utilisateur (sans mot de passe)."""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool


class TokenData(BaseModel):
    """Données encodées dans le JWT."""
    username: Optional[str] = None
    role: Optional[str] = None


class Token(BaseModel):
    """Réponse de l'endpoint de login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class LoginRequest(BaseModel):
    """Payload de connexion."""
    username: str
    password: str


class SocialProvider(str, Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class SocialLoginRequest(BaseModel):
    """Payload de connexion federée simplifiee."""
    provider: SocialProvider
    email: str = Field(..., min_length=5, max_length=120)
    full_name: str = Field(..., min_length=3, max_length=120)