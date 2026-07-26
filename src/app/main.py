"""Healthcare Voice Agent FastAPI Main Application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status, Depends
import uvicorn

from src.app.core.config import settings
from src.app.core.database import init_db, close_db
from src.app.core.logging import setup_logging, logger
from src.app.core.middleware import setup_middlewares, setup_exception_handlers
from src.app.api.v1.router import api_v1_router
from src.app.api.v1.endpoints import health, patients, calls, webhook

try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context managing startup and shutdown tasks."""
    # --- STARTUP ---
    setup_logging()
    logger.info("Starting Healthcare Voice Agent FastAPI backend...", env=settings.APP_ENV)
    try:
        await init_db()
    except Exception as exc:
        logger.warning("Database init skipped or deferred", error=str(exc))

    yield

    # --- SHUTDOWN ---
    logger.info("Shutting down Healthcare Voice Agent FastAPI backend...")
    await close_db()


def create_application() -> FastAPI:
    """Factory function to build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Production-Ready Healthcare Voice Agent REST API Backend",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {"name": "Root & Health", "description": "Core application root and health check endpoints"},
            {"name": "Patients", "description": "Patient record management, search, and filtering"},
            {"name": "Calls", "description": "Voice call logs, transcripts, and session analytics"},
            {"name": "Vapi Webhook", "description": "Webhook receiver for Vapi Voice AI callbacks"},
        ],
        lifespan=lifespan,
    )

    # Middleware Setup (CORS, GZip, TrustedHost, Security Headers, Rate Limiter, Trace & Correlation IDs)
    setup_middlewares(app)

    # Global Exception Handler Registration
    setup_exception_handlers(app)

    # GET / (Root Endpoint)
    @app.get("/", status_code=status.HTTP_200_OK, tags=["Root & Health"])
    async def root() -> dict[str, str]:
        """Root endpoint returning basic application metadata."""
        return {
            "app_name": settings.APP_NAME,
            "status": "running",
            "environment": settings.APP_ENV,
            "version": "0.1.0",
            "docs_url": "/docs",
            "api_v1": settings.API_V1_STR,
        }

    # Direct aliases for convenience (GET /health, GET /patients, GET /calls, POST /webhook/vapi)
    app.include_router(health.router, tags=["Root & Health"])
    app.include_router(patients.router)
    app.include_router(calls.router)
    app.include_router(webhook.router)

    # API v1 Prefix Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    # Expose Prometheus Metrics if configured
    if PROMETHEUS_AVAILABLE and settings.PROMETHEUS_METRICS_ENABLED:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)

    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "src.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
