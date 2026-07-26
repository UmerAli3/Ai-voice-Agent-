"""Vapi Webhook Endpoint Route Handler."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, Request, status

from src.app.api.deps import get_webhook_service
from src.app.schemas.common import ErrorResponse
from src.app.schemas.webhook import VapiWebhookResponse
from src.app.services.webhook_service import WebhookService

router = APIRouter(tags=["Vapi Webhook"])


@router.post(
    "/webhook/vapi",
    response_model=VapiWebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Vapi Webhook Callback",
    description=(
        "Ingests incoming end-of-call report webhooks from Vapi voice AI platform. "
        "Validates signature/secret header, extracts Conversation ID, Patient Name, DOB, Phone, "
        "Reason, and Summary, and stores the records in the database."
    ),
    responses={
        200: {"description": "Webhook payload received, verified, and stored successfully"},
        401: {"model": ErrorResponse, "description": "Invalid or missing webhook signature/secret"},
        422: {"model": ErrorResponse, "description": "Malformed JSON payload or schema validation failure"},
    },
)
async def handle_vapi_webhook(
    request: Request,
    payload: Dict[str, Any],
    x_vapi_secret: Optional[str] = Header(None, alias="x-vapi-secret"),
    x_vapi_signature: Optional[str] = Header(None, alias="x-vapi-signature"),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> VapiWebhookResponse:
    """POST /webhook/vapi - Ingest, validate, extract, and store Vapi call report payload."""
    raw_body = await request.body()
    secret_header = x_vapi_secret or x_vapi_signature

    return await webhook_service.process_webhook(
        payload=payload,
        secret_header=secret_header,
        raw_bytes=raw_body,
    )
