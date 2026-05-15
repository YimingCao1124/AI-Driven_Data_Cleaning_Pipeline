from fastapi import APIRouter

from ..config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "provider": settings.model_provider,
        "model": settings.model_name,
        "version": "0.1.0",
    }
