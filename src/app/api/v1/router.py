"""API v1 Central Router Aggregation."""

from fastapi import APIRouter
from src.app.api.v1.endpoints import calls, health, patients, webhook

api_v1_router = APIRouter()

# Include sub-routers with OpenAPI tags and prefix routing
api_v1_router.include_router(health.router)
api_v1_router.include_router(patients.router)
api_v1_router.include_router(calls.router)
api_v1_router.include_router(webhook.router)
