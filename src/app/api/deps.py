"""API dependency injections for routes, authentication, database sessions, repositories, and services."""

from typing import AsyncGenerator
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings
from src.app.core.database import get_db
from src.app.repositories.call_repository import CallRepository
from src.app.repositories.patient_repository import PatientRepository
from src.app.services.call_service import CallService
from src.app.services.patient_service import PatientService
from src.app.services.webhook_service import WebhookService

# Singleton repository instances (can easily be swapped with DB session-backed repos)
_patient_repo_instance = PatientRepository()
_call_repo_instance = CallRepository()


def get_patient_repository() -> PatientRepository:
    """Dependency provider for PatientRepository."""
    return _patient_repo_instance


def get_call_repository() -> CallRepository:
    """Dependency provider for CallRepository."""
    return _call_repo_instance


def get_patient_service(
    repo: PatientRepository = Depends(get_patient_repository),
) -> PatientService:
    """Dependency provider for PatientService."""
    return PatientService(patient_repo=repo)


def get_call_service(
    repo: CallRepository = Depends(get_call_repository),
) -> CallService:
    """Dependency provider for CallService."""
    return CallService(call_repo=repo)


def get_webhook_service(
    patient_repo: PatientRepository = Depends(get_patient_repository),
    call_repo: CallRepository = Depends(get_call_repository),
) -> WebhookService:
    """Dependency provider for WebhookService."""
    return WebhookService(patient_repo=patient_repo, call_repo=call_repo)


async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """Dependency to validate internal API keys for administrative endpoints."""
    if not x_api_key or x_api_key != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )
    return x_api_key


__all__ = [
    "get_db",
    "verify_api_key",
    "get_patient_repository",
    "get_call_repository",
    "get_patient_service",
    "get_call_service",
]
