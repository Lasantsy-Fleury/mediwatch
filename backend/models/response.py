from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """
    Enveloppe générique pour toutes les réponses de l'API.
    Garantit un format uniforme : { success, data, message, error }
    Le frontend peut toujours s'attendre à cette structure.
    """
    success: bool
    data: Optional[T] = None
    message: str = ""
    error: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Réponse paginée pour les listes longues"""
    items: list
    total: int
    page: int
    page_size: int
    has_next: bool