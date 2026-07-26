"""Common Pydantic Schemas for Pagination, Metadata, and API Responses."""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination, sorting, and searching."""

    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page (max 100)")
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc|ASC|DESC)$", description="Sort direction (asc or desc)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedMeta(BaseModel):
    """Pagination metadata response model."""

    page: int = Field(..., example=1, description="Current page number")
    page_size: int = Field(..., example=10, description="Number of items per page")
    total_items: int = Field(..., example=42, description="Total number of items found")
    total_pages: int = Field(..., example=5, description="Total number of pages")
    has_next: bool = Field(..., example=True, description="Whether a next page exists")
    has_prev: bool = Field(..., example=False, description="Whether a previous page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated API responses."""

    items: List[T]
    meta: PaginatedMeta


class ErrorDetail(BaseModel):
    """Standardized error detail schema."""

    code: str = Field(..., example="NOT_FOUND")
    message: str = Field(..., example="Resource not found")
    field: Optional[str] = Field(None, example="id")


class ErrorResponse(BaseModel):
    """Standardized top-level API error response body."""

    success: bool = Field(default=False, example=False)
    error: ErrorDetail
