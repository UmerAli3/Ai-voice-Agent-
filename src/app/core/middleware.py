"""Production Security Middleware, Correlation IDs, Rate Limiting, and Global Exception Handlers."""

import time
import uuid
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

import structlog
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.app.core.audit import log_audit_event
from src.app.core.config import settings
from src.app.core.logging import logger
from src.app.core.security_masking import mask_sensitive_payload


# =============================================================================
# In-Memory Rate Limiter (IP-based sliding window)
# =============================================================================
class RateLimiter:
    """In-memory sliding window rate limiter for protecting endpoints from abuse."""

    def __init__(self, requests_per_minute: int = 120, burst_limit: int = 200):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        # Filter out timestamps older than 60 seconds
        timestamps = [ts for ts in self.requests[client_ip] if ts > window_start]
        self.requests[client_ip] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            return True

        self.requests[client_ip].append(now)
        return False


global_rate_limiter = RateLimiter(requests_per_minute=180, burst_limit=300)


# =============================================================================
# Correlation & Request ID Middleware + Request Timing
# =============================================================================
class TraceAndCorrelationMiddleware(BaseHTTPMiddleware):
    """Injects correlation ID, request ID, timing, and structured logger context."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Trace-ID")
            or f"corr_{uuid.uuid4().hex[:12]}"
        )
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"

        request.state.correlation_id = correlation_id
        request.state.request_id = request_id

        # Bind context to structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )

        start_time = time.perf_counter()

        response = await call_next(request)

        process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-MS"] = str(process_time_ms)

        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            "http_request_finished",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=process_time_ms,
            client_ip=client_ip,
        )

        return response


# =============================================================================
# Security Headers Middleware
# =============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces essential production security headers on all outgoing HTTP responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers[
            "Content-Security-Policy"
        ] = "default-src 'self' http: https: data: blob: 'unsafe-inline'; frame-ancestors 'self';"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        return response


# =============================================================================
# Rate Limiting Middleware
# =============================================================================
class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware applying rate limits per IP address to non-exempt routes."""

    EXEMPT_PATHS = {"/health", "/api/v1/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        if global_rate_limiter.is_rate_limited(client_ip):
            correlation_id = getattr(request.state, "correlation_id", "unknown")
            logger.warning("rate_limit_exceeded", client_ip=client_ip, path=request.url.path)
            log_audit_event(
                action="RATE_LIMIT_EXCEEDED",
                resource_type="API_ENDPOINT",
                resource_id=request.url.path,
                actor_id=client_ip,
                status="BLOCKED",
                correlation_id=correlation_id,
                ip_address=client_ip,
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please slow down and try again shortly.",
                        "correlation_id": correlation_id,
                    }
                },
                headers={"Retry-After": "60"},
            )

        return await call_next(request)


# =============================================================================
# Setup Function for Middlewares
# =============================================================================
def setup_middlewares(app: FastAPI) -> None:
    """Register all security, timing, compression, host, and trace middlewares."""

    # 1. Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "*.internexus.tech", "internexus.tech", "*"],
    )

    # 2. GZip Compression Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 3. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 4. Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # 5. Rate Limiting Middleware
    app.add_middleware(RateLimitingMiddleware)

    # 6. Trace & Correlation ID Middleware (executed first in request flow)
    app.add_middleware(TraceAndCorrelationMiddleware)


# =============================================================================
# Global Exception Handlers
# =============================================================================
def setup_exception_handlers(app: FastAPI) -> None:
    """Register robust, production-grade exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        sanitized_errors = mask_sensitive_payload(exc.errors())

        logger.warning(
            "request_validation_failed",
            path=request.url.path,
            errors=sanitized_errors,
            correlation_id=correlation_id,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload or query parameters.",
                    "details": sanitized_errors,
                    "correlation_id": correlation_id,
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        logger.warning(
            "http_exception",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            correlation_id=correlation_id,
        )

        detail_content = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
        if "correlation_id" not in detail_content:
            detail_content["correlation_id"] = correlation_id

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": detail_content},
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        client_ip = request.client.host if request.client else "unknown"

        logger.error(
            "unhandled_exception",
            error=str(exc),
            path=request.url.path,
            method=request.method,
            correlation_id=correlation_id,
            exc_info=True,
        )

        log_audit_event(
            action="UNHANDLED_EXCEPTION",
            resource_type="API_ENDPOINT",
            resource_id=request.url.path,
            actor_id=client_ip,
            status="ERROR",
            correlation_id=correlation_id,
            ip_address=client_ip,
            details={"error_class": exc.__class__.__name__, "error_message": str(exc)},
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred. Please contact system support.",
                    "correlation_id": correlation_id,
                }
            },
        )
