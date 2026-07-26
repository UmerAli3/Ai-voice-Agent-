"""Call Logs REST API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from src.app.api.deps import get_call_service
from src.app.schemas.call import CallFilterParams, CallRead, CallStatusEnum, CallTypeEnum
from src.app.schemas.common import ErrorResponse, PaginatedResponse, PaginationParams
from src.app.services.call_service import CallService

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.get(
    "",
    response_model=PaginatedResponse[CallRead],
    status_code=status.HTTP_200_OK,
    summary="List call logs",
    description="Retrieve a paginated list of call logs with filtering by patient, status, and call type.",
    responses={
        200: {"description": "Paginated call logs returned successfully"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
    },
)
async def list_calls(
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by (e.g. created_at, duration_seconds, cost)"),
    sort_order: str = Query("desc", pattern="^(asc|desc|ASC|DESC)$", description="Sort order"),
    patient_id: Optional[str] = Query(None, description="Filter calls by associated patient ID"),
    status_filter: Optional[CallStatusEnum] = Query(None, alias="status", description="Filter by call status"),
    call_type: Optional[CallTypeEnum] = Query(None, description="Filter by call type (inbound/outbound)"),
    min_duration: Optional[int] = Query(None, ge=0, description="Minimum call duration in seconds"),
    service: CallService = Depends(get_call_service),
) -> PaginatedResponse[CallRead]:
    """GET /calls - Retrieve paginated list of call records."""
    pagination = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    filters = CallFilterParams(
        patient_id=patient_id,
        status=status_filter,
        call_type=call_type,
        min_duration=min_duration,
    )
    return await service.get_calls_paginated(pagination=pagination, filters=filters)


@router.get(
    "/{id}",
    response_model=CallRead,
    status_code=status.HTTP_200_OK,
    summary="Get call log details",
    description="Fetch a specific call log record by unique ID.",
    responses={
        200: {"description": "Call log record found and returned"},
        404: {"model": ErrorResponse, "description": "Call record not found"},
    },
)
async def get_call(
    id: str,
    service: CallService = Depends(get_call_service),
) -> CallRead:
    """GET /calls/{id} - Retrieve call details by ID."""
    return await service.get_call_by_id(id)
