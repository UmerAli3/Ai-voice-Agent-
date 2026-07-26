"""Health router providing health checks, readiness probes, and liveness probes."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.database import get_db
from src.app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health Checks"])


class HealthStatus(BaseModel):
    status: str
    environment: str
    version: str
    database: str


@router.get("", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthStatus:
    """Comprehensive service health check verifying DB connectivity."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return HealthStatus(
        status="ok" if db_status == "healthy" else "degraded",
        environment=settings.APP_ENV,
        version="0.1.0",
        database=db_status,
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_probe() -> dict[str, str]:
    """Kubernetes / Docker readiness probe endpoint."""
    return {"status": "ready"}


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> dict[str, str]:
    """Kubernetes / Docker liveness probe endpoint."""
    return {"status": "alive"}
