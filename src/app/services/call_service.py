"""Call Business Logic Service."""

from fastapi import HTTPException, status

from src.app.core.logging import logger
from src.app.repositories.call_repository import CallRepository
from src.app.schemas.call import CallCreate, CallFilterParams, CallRead, CallUpdate
from src.app.schemas.common import PaginatedMeta, PaginatedResponse, PaginationParams


class CallService:
    """Service handling Call Log operations and business logic."""

    def __init__(self, call_repo: CallRepository):
        self.call_repo = call_repo

    async def get_call_by_id(self, call_id: str) -> CallRead:
        """Fetch call log by ID with 404 validation."""
        logger.info("Fetching call log details", call_id=call_id)
        call_log = await self.call_repo.get_by_id(call_id)
        if not call_log:
            logger.warning("Call log record not found", call_id=call_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CALL_NOT_FOUND",
                    "message": f"Call record with ID '{call_id}' was not found.",
                },
            )
        return call_log

    async def get_calls_paginated(
        self,
        pagination: PaginationParams,
        filters: CallFilterParams,
    ) -> PaginatedResponse[CallRead]:
        """Fetch paginated call records with filtering and sorting."""
        logger.info(
            "Listing call logs",
            page=pagination.page,
            page_size=pagination.page_size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )

        items, total_count = await self.call_repo.list_calls(
            filters=filters,
            offset=pagination.offset,
            limit=pagination.page_size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )

        total_pages = max(1, (total_count + pagination.page_size - 1) // pagination.page_size)

        meta = PaginatedMeta(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total_count,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1,
        )

        return PaginatedResponse[CallRead](items=items, meta=meta)

    async def create_call(self, payload: CallCreate) -> CallRead:
        """Create a new call log entry."""
        logger.info("Recording call session", patient_id=payload.patient_id, status=payload.status)
        call_log = await self.call_repo.create(payload)
        return call_log

    async def update_call(self, call_id: str, payload: CallUpdate) -> CallRead:
        """Update existing call session."""
        await self.get_call_by_id(call_id)
        updated_call = await self.call_repo.update(call_id, payload)
        if not updated_call:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "UPDATE_FAILED", "message": "Failed to update call log record."},
            )
        return updated_call
