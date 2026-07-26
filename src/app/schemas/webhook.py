"""Vapi Webhook Schemas for Payload Validation and Data Extraction."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VapiEventType(str, Enum):
    END_OF_CALL_REPORT = "end-of-call-report"
    TRANSCRIPT = "transcript"
    FUNCTION_CALL = "function-call"
    STATUS_UPDATE = "status-update"
    SPEECH_UPDATE = "speech-update"


class VapiCustomer(BaseModel):
    number: Optional[str] = Field(None, example="+15550192834")
    name: Optional[str] = Field(None, example="Eleanor Vance")


class VapiArtifact(BaseModel):
    transcript: Optional[str] = Field(None, example="Agent: Hello Eleanor. Patient: Hi, confirming appointment.")
    recordingUrl: Optional[str] = Field(None, example="https://api.vapi.ai/recordings/call_123.mp3")


class VapiAnalysis(BaseModel):
    summary: Optional[str] = Field(None, example="Patient confirmed appointment and asked about prescription refill.")
    structuredData: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        example={"dob": "1982-04-15", "reason": "Appointment Confirmation", "patient_name": "Eleanor Vance"},
    )


class VapiCallObject(BaseModel):
    id: str = Field(..., example="call_conv_99812", description="Vapi Conversation / Call ID")
    status: Optional[str] = Field(None, example="ended")
    type: Optional[str] = Field(None, example="inboundPhoneCall")
    customer: Optional[VapiCustomer] = None
    artifact: Optional[VapiArtifact] = None
    analysis: Optional[VapiAnalysis] = None


class VapiWebhookMessage(BaseModel):
    type: str = Field(..., example="end-of-call-report")
    call: Optional[VapiCallObject] = None
    timestamp: Optional[int] = None


class VapiWebhookPayload(BaseModel):
    """Top-level Vapi webhook request payload model."""

    message: VapiWebhookMessage


class ExtractedVapiData(BaseModel):
    """Extracted normalized fields from Vapi Webhook for storage."""

    conversation_id: str = Field(..., example="call_conv_99812")
    patient_name: Optional[str] = Field(None, example="Eleanor Vance")
    dob: Optional[str] = Field(None, example="1982-04-15")
    phone: Optional[str] = Field(None, example="+15550192834")
    reason: Optional[str] = Field(None, example="Cardiology Appointment Confirmation")
    summary: Optional[str] = Field(None, example="Patient confirmed appointment for tomorrow at 10 AM.")
    transcript: Optional[str] = Field(None, example="Agent: Hello Eleanor...")


class VapiWebhookResponse(BaseModel):
    """Standard success response for Vapi Webhook endpoint."""

    status: str = Field(default="success", example="success")
    message: str = Field(default="Webhook payload processed and stored successfully")
    conversation_id: str = Field(..., example="call_conv_99812")
    extracted_data: ExtractedVapiData
