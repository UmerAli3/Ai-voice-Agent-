"""Patient REST API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from src.app.api.deps import get_patient_service
from src.app.schemas.common import ErrorResponse, PaginatedResponse, PaginationParams
from src.app.schemas.patient import PatientFilterParams, PatientRead
from src.app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get(
    "",
    response_model=PaginatedResponse[PatientRead],
    status_code=status.HTTP_200_OK,
    summary="List patients",
    description="Retrieve a paginated list of patients with search, filtering, and sorting support.",
    responses={
        200: {"description": "Paginated list of patients returned successfully"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
    },
)
async def list_patients(
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by (e.g. created_at, first_name, last_name)"),
    sort_order: str = Query("desc", pattern="^(asc|desc|ASC|DESC)$", description="Sort order"),
    search: Optional[str] = Query(None, description="Search keyword in name, phone, or email"),
    is_active: Optional[bool] = Query(None, description="Filter active or inactive status"),
    preferred_language: Optional[str] = Query(None, description="Filter by preferred language code (e.g., 'en', 'es')"),
    service: PatientService = Depends(get_patient_service),
) -> PaginatedResponse[PatientRead]:
    """GET /patients - Retrieve paginated patients list."""
    pagination = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    filters = PatientFilterParams(
        search=search,
        is_active=is_active,
        preferred_language=preferred_language,
    )
    return await service.get_patients_paginated(pagination=pagination, filters=filters)


@router.get(
    "/{id}",
    response_model=PatientRead,
    status_code=status.HTTP_200_OK,
    summary="Get patient details",
    description="Fetch a single patient by unique ID.",
    responses={
        200: {"description": "Patient record found and returned"},
        404: {"model": ErrorResponse, "description": "Patient not found"},
    },
)
async def get_patient(
    id: str,
    service: PatientService = Depends(get_patient_service),
) -> PatientRead:
    """GET /patients/{id} - Retrieve patient details by ID."""
    return await service.get_patient_by_id(id)
