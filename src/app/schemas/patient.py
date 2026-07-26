"""Patient Schemas for Validation and Response Serialization."""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, example="Eleanor")
    last_name: str = Field(..., min_length=1, max_length=100, example="Vance")
    phone_number: str = Field(..., min_length=7, max_length=20, example="+15550192834")
    email: Optional[EmailStr] = Field(None, example="eleanor.vance@example.com")
    date_of_birth: Optional[date] = Field(None, example="1982-04-15")
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN, example="female")
    preferred_language: str = Field(default="en", max_length=10, example="en")
    address: Optional[str] = Field(None, example="742 Evergreen Terrace, Springfield")
    is_active: bool = Field(default=True, example=True)


class PatientCreate(PatientBase):
    """Schema for creating a patient."""

    pass


class PatientUpdate(BaseModel):
    """Schema for partial update of a patient."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    preferred_language: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class PatientRead(PatientBase):
    """Schema for reading patient details."""

    id: str = Field(..., example="pat_98231023")
    created_at: datetime = Field(..., example="2026-07-26T10:00:00Z")
    updated_at: datetime = Field(..., example="2026-07-26T10:00:00Z")

    class Config:
        from_attributes = True


class PatientFilterParams(BaseModel):
    """Query parameter filter schema for patients."""

    search: Optional[str] = Field(None, description="Search by name, phone, or email")
    is_active: Optional[bool] = Field(None, description="Filter active/inactive patients")
    preferred_language: Optional[str] = Field(None, description="Filter by language code")
