"""Vapi Webhook Service for payload validation, signature verification, extraction, and storage."""

import hmac
import hashlib
from typing import Any, Dict, Optional
from fastapi import HTTPException, status

from src.app.core.audit import log_audit_event
from src.app.core.config import settings
from src.app.core.logging import logger
from src.app.core.security_masking import mask_dob, mask_phone_number
from src.app.repositories.call_repository import CallRepository
from src.app.repositories.patient_repository import PatientRepository
from src.app.schemas.call import CallCreate, CallStatusEnum, CallTypeEnum
from src.app.schemas.patient import PatientCreate
from src.app.schemas.webhook import ExtractedVapiData, VapiWebhookResponse


class WebhookService:
    """Service handling Vapi Webhook processing, signature validation, extraction, and storage."""

    def __init__(self, patient_repo: PatientRepository, call_repo: CallRepository):
        self.patient_repo = patient_repo
        self.call_repo = call_repo

    def verify_vapi_signature(self, secret_header: Optional[str], raw_payload_bytes: bytes) -> bool:
        """Verify incoming webhook secret or signature if configured in settings."""
        expected_secret = settings.VAPI_WEBHOOK_SECRET
        if not expected_secret or expected_secret in ["whsec_your_webhook_secret_here", ""]:
            # If default template secret, skip strict rejection in dev mode but log notice
            logger.debug("Vapi webhook secret check bypassed or using development setting")
            return True

        if not secret_header:
            logger.warning("Missing x-vapi-secret or signature header in webhook request")
            return False

        # Constant time secret string comparison
        return hmac.compare_digest(secret_header, expected_secret)

    def extract_vapi_fields(self, payload: Dict[str, Any]) -> ExtractedVapiData:
        """Extract Conversation ID, Patient Name, DOB, Phone, Reason, and Summary from Vapi payload."""
        message = payload.get("message", {})
        call = message.get("call", {}) if isinstance(message, dict) else {}
        customer = call.get("customer", {}) if isinstance(call, dict) else {}
        artifact = call.get("artifact", {}) if isinstance(call, dict) else {}
        analysis = call.get("analysis", {}) if isinstance(call, dict) else {}
        structured_data = analysis.get("structuredData", {}) if isinstance(analysis, dict) else {}

        # 1. Conversation ID / Call ID
        conversation_id = call.get("id") or payload.get("call_id") or payload.get("id") or "conv_unknown"

        # 2. Patient Name
        patient_name = (
            structured_data.get("patient_name")
            or customer.get("name")
            or payload.get("patient_name")
            or "Unknown Patient"
        )

        # 3. DOB (Date of Birth)
        dob = (
            structured_data.get("dob")
            or structured_data.get("date_of_birth")
            or payload.get("dob")
        )

        # 4. Phone
        phone = (
            customer.get("number")
            or payload.get("phone")
            or payload.get("phone_number")
            or "+15550000000"
        )

        # 5. Reason
        reason = (
            structured_data.get("reason")
            or structured_data.get("call_reason")
            or analysis.get("reason")
            or payload.get("reason")
            or "General Healthcare Query"
        )

        # 6. Summary
        summary = (
            analysis.get("summary")
            or payload.get("summary")
            or artifact.get("transcript")
            or "Call completed with Vapi Voice Agent."
        )

        transcript = artifact.get("transcript") or payload.get("transcript")

        return ExtractedVapiData(
            conversation_id=conversation_id,
            patient_name=patient_name,
            dob=str(dob) if dob else None,
            phone=phone,
            reason=reason,
            summary=summary,
            transcript=transcript,
        )

    async def process_webhook(
        self,
        payload: Dict[str, Any],
        secret_header: Optional[str] = None,
        raw_bytes: bytes = b"",
    ) -> VapiWebhookResponse:
        """Process incoming Vapi webhook: validate signature, extract fields, and store data."""
        logger.info("Received incoming Vapi webhook request")

        # Signature / Secret Verification
        if not self.verify_vapi_signature(secret_header, raw_bytes):
            logger.error("Vapi webhook signature verification failed")
            log_audit_event(
                action="VAPI_WEBHOOK_AUTH_FAILED",
                resource_type="WEBHOOK",
                resource_id="vapi_webhook",
                status="UNAUTHORIZED",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED_WEBHOOK",
                    "message": "Invalid or missing x-vapi-secret / signature header",
                },
            )

        # Field Extraction
        extracted = self.extract_vapi_fields(payload)
        logger.info(
            "Extracted Vapi webhook fields",
            conversation_id=extracted.conversation_id,
            patient_name=extracted.patient_name,
            phone=mask_phone_number(extracted.phone or ""),
            dob=mask_dob(extracted.dob or ""),
            reason=extracted.reason,
        )

        # Split patient name into first/last name
        name_parts = (extracted.patient_name or "Patient").split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "User"

        # Store Patient data
        patient_record = await self.patient_repo.create(
            PatientCreate(
                first_name=first_name,
                last_name=last_name,
                phone_number=extracted.phone or "+15550190000",
                preferred_language="en",
            )
        )

        # Store Call Log data
        call_record = await self.call_repo.create(
            CallCreate(
                patient_id=patient_record.id,
                call_type=CallTypeEnum.INBOUND,
                status=CallStatusEnum.COMPLETED,
                vapi_call_id=extracted.conversation_id,
                summary=f"[{extracted.reason}] {extracted.summary}",
                transcript=extracted.transcript,
                metadata={
                    "extracted_dob": extracted.dob,
                    "extracted_reason": extracted.reason,
                    "vapi_conversation_id": extracted.conversation_id,
                },
            )
        )

        logger.info(
            "Vapi webhook data stored successfully",
            patient_id=patient_record.id,
            call_id=call_record.id,
            conversation_id=extracted.conversation_id,
        )

        log_audit_event(
            action="VAPI_WEBHOOK_PROCESSED",
            resource_type="CALL_RECORD",
            resource_id=extracted.conversation_id,
            actor_id="vapi_voice_agent",
            status="SUCCESS",
            details={
                "patient_id": patient_record.id,
                "call_id": call_record.id,
                "reason": extracted.reason,
            },
        )

        return VapiWebhookResponse(
            status="success",
            message="Vapi webhook payload parsed, verified, and stored successfully",
            conversation_id=extracted.conversation_id,
            extracted_data=extracted,
        )
