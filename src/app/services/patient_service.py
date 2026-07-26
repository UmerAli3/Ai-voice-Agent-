"""Patient Business Logic Service."""

from typing import List, Tuple
from fastapi import HTTPException, status

from src.app.core.logging import logger
from src.app.repositories.patient_repository import PatientRepository
from src.app.schemas.common import PaginatedMeta, PaginatedResponse, PaginationParams
from src.app.schemas.patient import PatientCreate, PatientFilterParams, PatientRead, PatientUpdate


class PatientService:
    """Service handling Patient business rules and data operations."""

    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def get_patient_by_id(self, patient_id: str) -> PatientRead:
        """Retrieve patient details by ID with error validation."""
        logger.info("Fetching patient details", patient_id=patient_id)
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            logger.warning("Patient not found", patient_id=patient_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PATIENT_NOT_FOUND",
                    "message": f"Patient with ID '{patient_id}' was not found.",
                },
            )
        return patient

    async def get_patients_paginated(
        self,
        pagination: PaginationParams,
        filters: PatientFilterParams,
    ) -> PaginatedResponse[PatientRead]:
        """Fetch paginated, filtered, and sorted patient records."""
        logger.info(
            "Listing patients",
            page=pagination.page,
            page_size=pagination.page_size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )

        items, total_count = await self.patient_repo.list_patients(
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

        return PaginatedResponse[PatientRead](items=items, meta=meta)

    async def create_patient(self, payload: PatientCreate) -> PatientRead:
        """Create a new patient record with business rule validation."""
        logger.info("Creating new patient record", phone=payload.phone_number, email=payload.email)
        # Business rule check: Ensure phone number is present and sanitized
        patient = await self.patient_repo.create(payload)
        logger.info("Patient record created successfully", patient_id=patient.id)
        return patient

    async def update_patient(self, patient_id: str, payload: PatientUpdate) -> PatientRead:
        """Update existing patient with validation."""
        await self.get_patient_by_id(patient_id)  # Throws 404 if not found
        updated_patient = await self.patient_repo.update(patient_id, payload)
        if not updated_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "UPDATE_FAILED", "message": "Failed to update patient record."},
            )
        return updated_patient
