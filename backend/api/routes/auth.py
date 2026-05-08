from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from models.auth import Token, LoginRequest, UserCreate, UserRead, SocialLoginRequest, UserRole
from models.response import APIResponse
from utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    get_user,
    _users_db,
)
from utils.config import settings
import uuid

router = APIRouter()


@router.post(
    "/auth/login",
    response_model=Token,
    summary="Connexion et obtention du token JWT"
)
async def login(credentials: LoginRequest):
    """
    Authentifie un utilisateur et retourne un JWT.
    Le token doit être inclus dans toutes les requêtes suivantes :
    Header : Authorization: Bearer <token>
    """
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserRead(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            is_active=user["is_active"]
        )
    )


@router.get(
    "/auth/me",
    response_model=APIResponse,
    summary="Profil de l'utilisateur connecté"
)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retourne les informations de l'utilisateur authentifié."""
    user_data = UserRead(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        is_active=current_user["is_active"]
    )
    return APIResponse(
        success=True,
        data=user_data.model_dump(),
        message=f"Connecté en tant que {current_user['full_name']}"
    )


@router.post(
    "/auth/register",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau compte praticien"
)
async def register(user_data: UserCreate):
    """
    Crée un nouveau compte praticien.
    Pour limiter les privilèges, le rôle est forcé à doctor.
    """
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"L'utilisateur '{user_data.username}' existe déjà"
        )

    email_already_used = any(
        user["email"].lower() == user_data.email.lower()
        for user in _users_db.values()
    )
    if email_already_used:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"L'email '{user_data.email}' est déjà utilisé"
        )

    new_user = {
        "id": str(uuid.uuid4()),
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hash_password(user_data.password),
        "role": UserRole.DOCTOR,
        "is_active": True
    }
    _users_db[user_data.username] = new_user

    return APIResponse(
        success=True,
        data=UserRead(**{k: v for k, v in new_user.items()
                        if k != "hashed_password"}).model_dump(),
        message=f"Utilisateur {user_data.full_name} créé avec succès"
    )


@router.post(
    "/auth/social-login",
    response_model=Token,
    summary="Connexion via fournisseur externe (Google/Microsoft)"
)
async def social_login(payload: SocialLoginRequest):
    """
    Connexion federée simplifiée.
    Si le compte n'existe pas encore, il est créé automatiquement.
    """
    provider_prefix = payload.provider.value
    sanitized_email = payload.email.lower()

    matched_user = next(
        (user for user in _users_db.values() if user["email"].lower() == sanitized_email),
        None
    )

    if matched_user is None:
        suggested_username = f"{provider_prefix}_{sanitized_email.split('@')[0]}"
        candidate_username = suggested_username
        suffix = 1
        while get_user(candidate_username):
            suffix += 1
            candidate_username = f"{suggested_username}{suffix}"

        matched_user = {
            "id": str(uuid.uuid4()),
            "username": candidate_username,
            "email": sanitized_email,
            "full_name": payload.full_name,
            "hashed_password": hash_password(str(uuid.uuid4())),
            "role": UserRole.DOCTOR,
            "is_active": True,
        }
        _users_db[candidate_username] = matched_user

    access_token = create_access_token(
        data={"sub": matched_user["username"], "role": matched_user["role"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserRead(
            id=matched_user["id"],
            username=matched_user["username"],
            email=matched_user["email"],
            full_name=matched_user["full_name"],
            role=matched_user["role"],
            is_active=matched_user["is_active"]
        )
    )


@router.post(
    "/auth/logout",
    response_model=APIResponse,
    summary="Déconnexion"
)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Déconnexion côté client.
    Avec JWT stateless, la déconnexion réelle se fait côté frontend
    en supprimant le token du localStorage.
    """
    return APIResponse(
        success=True,
        message=f"Au revoir, {current_user['full_name']}"
    )