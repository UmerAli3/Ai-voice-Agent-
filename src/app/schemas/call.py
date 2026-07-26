"""Call Log Schemas for Validation and API Responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CallTypeEnum(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatusEnum(str, Enum):
    QUEUED = "queued"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"


class CallBase(BaseModel):
    patient_id: str = Field(..., example="pat_98231023", description="Associated patient ID")
    call_type: CallTypeEnum = Field(default=CallTypeEnum.INBOUND, example="inbound")
    status: CallStatusEnum = Field(default=CallStatusEnum.COMPLETED, example="completed")
    vapi_call_id: Optional[str] = Field(None, example="vapi_call_882310")
    duration_seconds: int = Field(default=0, ge=0, example=145)
    summary: Optional[str] = Field(None, example="Patient confirmed appointment for tomorrow at 10 AM.")
    transcript: Optional[str] = Field(None, example="Agent: Hello Eleanor. Patient: Hi, I am calling to confirm my appointment.")
    recording_url: Optional[str] = Field(None, example="https://api.vapi.ai/recordings/call_882310.mp3")
    cost: float = Field(default=0.0, ge=0.0, example=0.12)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CallCreate(CallBase):
    """Schema for recording a new call."""

    pass


class CallUpdate(BaseModel):
    """Schema for updating a call record."""

    status: Optional[CallStatusEnum] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    summary: Optional[str] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    cost: Optional[float] = Field(None, ge=0.0)
    metadata: Optional[Dict[str, Any]] = None


class CallRead(CallBase):
    """Schema for reading call logs."""

    id: str = Field(..., example="call_1092384")
    started_at: datetime = Field(..., example="2026-07-26T14:30:00Z")
    ended_at: Optional[datetime] = Field(None, example="2026-07-26T14:32:25Z")
    created_at: datetime = Field(..., example="2026-07-26T14:30:00Z")

    class Config:
        from_attributes = True


class CallFilterParams(BaseModel):
    """Query parameters for filtering calls."""

    patient_id: Optional[str] = Field(None, description="Filter calls by patient ID")
    status: Optional[CallStatusEnum] = Field(None, description="Filter calls by status")
    call_type: Optional[CallTypeEnum] = Field(None, description="Filter inbound/outbound calls")
    min_duration: Optional[int] = Field(None, ge=0, description="Minimum call duration in seconds")
