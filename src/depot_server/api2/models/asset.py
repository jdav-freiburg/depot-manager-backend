from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AssetBase(BaseModel):
    """Base asset schema."""

    description: Optional[str] = None
    required_role: str = "user"


class AssetUpload(BaseModel):
    """Asset upload request."""

    asset_type: str
    required_role: str = "user"
    description: Optional[str] = None


class AssetUpdate(BaseModel):
    """Asset update request."""

    description: Optional[str] = None
    required_role: Optional[str] = None
    data: Optional[dict] = None


class AssetMetadata(BaseModel):
    """Asset metadata response."""

    id: UUID
    uri: str
    sha256: str
    mimetype: str
    asset_type: str
    required_role: str
    original_filename: Optional[str]
    description: Optional[str]
    created_at: datetime
    created_by: UUID
    updated_at: datetime
    updated_by: UUID
    data: Optional[dict]

    class Config:
        from_attributes = True


class AssetResponse(BaseModel):
    """Asset response after creation."""

    id: UUID
    uri: str
    sha256: str
    mimetype: str
    asset_type: str
    required_role: str
    original_filename: Optional[str]
    description: Optional[str]
    created_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


class AssetList(BaseModel):
    """Paginated asset list."""

    items: list[AssetMetadata]
    total: int
    page: int
    page_size: int
    pages: int


class DuplicateError(BaseModel):
    """Duplicate file error response."""

    error: str = "DUPLICATE_FILE"
    message: str
    existing_asset: AssetMetadata


class NotFoundError(BaseModel):
    """Not found error response."""

    error: str = "NOT_FOUND"
    message: str


class OrphanedFilesReport(BaseModel):
    """Report from orphaned files cleanup."""

    scanned: int
    missing_files: list[dict]
    recovered: int
    deleted: Optional[int] = None
