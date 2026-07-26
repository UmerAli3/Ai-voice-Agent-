"""Audit Logging Module for HIPAA/Healthcare Security Compliance."""

from typing import Any, Dict, Optional
import structlog
from src.app.core.security_masking import mask_sensitive_payload

audit_logger = structlog.get_logger("healthcare_audit_event")


def log_audit_event(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    actor_id: Optional[str] = "system",
    status: str = "SUCCESS",
    correlation_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log structured security and HIPAA compliance audit event with sensitive data masking."""
    sanitized_details = mask_sensitive_payload(details) if details else {}

    audit_logger.info(
        "AUDIT_EVENT",
        audit_event_type="AUDIT",
        action=action,
        resource_type=resource_type,
        resource_id=resource_id or "N/A",
        actor_id=actor_id or "system",
        status=status,
        correlation_id=correlation_id or "N/A",
        client_ip=ip_address or "N/A",
        details=sanitized_details,
    )
