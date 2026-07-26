"""Sensitive Data Masking Utility for PHI and PII Protection in Logs and Audit Events."""

import re
from typing import Any, Dict, List, Union


def mask_phone_number(phone: str) -> str:
    """Mask phone number leaving country code and last 4 digits visible."""
    if not phone or len(phone) < 7:
        return "***-***-****"
    clean = re.sub(r"[^\d+]", "", phone)
    if len(clean) > 4:
        return f"{clean[:3]}***{clean[-4:]}"
    return "***-***-****"


def mask_dob(dob: str) -> str:
    """Mask Date of Birth preserving only birth year."""
    if not dob:
        return "****-**-**"
    dob_str = str(dob).strip()
    match = re.search(r"(\d{4})", dob_str)
    if match:
        return f"{match.group(1)}-XX-XX"
    return "****-**-**"


def mask_email(email: str) -> str:
    """Mask email address showing first character and domain."""
    if not email or "@" not in email:
        return "*@****.***"
    user, domain = email.split("@", 1)
    masked_user = f"{user[0]}***" if len(user) > 1 else "*"
    return f"{masked_user}@{domain}"


def mask_token(token: str) -> str:
    """Mask authentication token or secret key."""
    if not token or len(token) < 8:
        return "********"
    return f"{token[:4]}****{token[-4:]}"


def mask_sensitive_payload(data: Union[Dict[str, Any], List[Any], str, Any]) -> Any:
    """Recursively traverse dict/list and mask sensitive fields (PHI, PII, Tokens)."""
    if isinstance(data, dict):
        masked_dict = {}
        for key, value in data.items():
            key_lower = key.lower()
            if key_lower in ["dob", "date_of_birth", "birthdate"]:
                masked_dict[key] = mask_dob(str(value)) if value else value
            elif key_lower in ["phone", "phone_number", "mobile", "telephone"]:
                masked_dict[key] = mask_phone_number(str(value)) if value else value
            elif key_lower in ["email", "email_address"]:
                masked_dict[key] = mask_email(str(value)) if value else value
            elif key_lower in ["ssn", "social_security_number"]:
                masked_dict[key] = "***-XX-****"
            elif key_lower in ["secret", "vapi_webhook_secret", "token", "password", "api_key", "authorization"]:
                masked_dict[key] = mask_token(str(value)) if value else value
            else:
                masked_dict[key] = mask_sensitive_payload(value)
        return masked_dict
    elif isinstance(data, list):
        return [mask_sensitive_payload(item) for item in data]
    return data
