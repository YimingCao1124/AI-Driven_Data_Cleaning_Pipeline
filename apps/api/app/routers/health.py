from fastapi import APIRouter

from ..config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict:
    model = (
        settings.anthropic_model
        if settings.model_provider == "anthropic"
        else settings.model_name
    )
    return {
        "status": "ok",
        "provider": settings.model_provider,
        "model": model,
        "version": "0.1.0",
    }
