from typing import Optional, TypedDict
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse

from depot_server.api2.models.asset import (
    AssetMetadata, AssetResponse, AssetUpdate, AssetList, OrphanedFilesReport
)
from depot_server.db2.models.asset import Asset, AssetType, AllowedMimeType
from depot_server.logic.asset_service import (
    AssetService, AssetNotFoundError, AccessDeniedError, FileTooLargeError,
    MimetypeNotAllowedError, DuplicateFileError, StorageBackendError
)
from depot_server.logic.storage.factory import StorageFactory
from depot_server.config import config


class CurrentUser(TypedDict):
    """Current authenticated user context."""
    user_id: UUID
    role: str


router = APIRouter(prefix="/assets", tags=["assets"])

# Singleton asset service instance
_asset_service: Optional[AssetService] = None


def get_asset_service() -> AssetService:
    """Get or create the asset service singleton."""
    global _asset_service
    if _asset_service is None:
        storage_factory = StorageFactory(
            local_path=config.storage.local_path,
            s3_bucket=config.storage.s3_bucket,
            s3_region=config.storage.s3_region,
        )
        _asset_service = AssetService(storage_factory)
    return _asset_service


async def get_current_user() -> CurrentUser:
    """Stub dependency for current user. Implement with your auth logic."""
    # TODO: Implement actual authentication with your auth system
    return CurrentUser(user_id=UUID(int=1), role="user")


@router.post("/", status_code=201, response_model=AssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    required_role: str = Form(default="user"),
    description: Optional[str] = Form(default=None),
    current_user: CurrentUser = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """Upload a new asset."""
    try:
        # Get asset type UUID from name
        asset_type_obj = await AssetType.get_or_none(name=asset_type)
        if not asset_type_obj:
            raise HTTPException(status_code=400, detail=f"Unknown asset type: {asset_type}")

        # Validate MIME type
        mime_obj = await AllowedMimeType.get_or_none(mime=file.content_type)
        if not mime_obj:
            raise MimetypeNotAllowedError(f"MIME type {file.content_type} not allowed")

        asset = await service.upload_asset(
            file=file,
            asset_type_id=asset_type_obj.id,
            required_role=required_role,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
            description=description,
        )

        return AssetResponse(
            id=asset.id,
            uri=asset.uri,
            sha256=asset.hash_,
            mimetype=mime_obj.mime,
            asset_type=asset_type,
            required_role=asset.required_role,
            original_filename=asset.original_filename,
            description=asset.description,
            created_at=asset.created_at,
            created_by=asset.created_by,
        )

    except MimetypeNotAllowedError:
        raise HTTPException(status_code=415, detail="MIME type not allowed")
    except FileTooLargeError:
        raise HTTPException(status_code=413, detail="File too large")
    except DuplicateFileError:
        raise HTTPException(status_code=409, detail="File with same content already exists (DUPLICATE_FILE)")
    except StorageBackendError:
        raise HTTPException(status_code=500, detail="Storage backend unavailable")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Only managers and admins can upload")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{asset_id}")
async def download_asset(
    asset_id: UUID,
    download: bool = Query(False),
    current_user: CurrentUser = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """Download asset content."""
    try:
        content = await service.get_asset_bytes(
            asset_id=asset_id,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
        )

        asset = await Asset.get_or_none(id=asset_id)
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")

        headers = {}
        if download and asset.original_filename:
            headers["Content-Disposition"] = f'attachment; filename="{asset.original_filename}"'

        # Get MIME type from database
        mime_type = "application/octet-stream"
        if asset.mime:
            mime_type = asset.mime

        return StreamingResponse(
            iter([content]),
            media_type=mime_type,
            headers=headers,
        )

    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")
    except FileNotFoundError:
        raise HTTPException(status_code=410, detail="File missing from storage")


@router.get("/{asset_id}/metadata", response_model=AssetMetadata)
async def get_asset_metadata(
    asset_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """Get asset metadata without content."""
    try:
        asset = await service.get_asset_metadata(
            asset_id=asset_id,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
        )

        # Get asset type name
        asset_type_obj = await asset.asset_type
        asset_type_name = asset_type_obj.name if asset_type_obj else "unknown"

        return AssetMetadata(
            id=asset.id,
            uri=asset.uri,
            sha256=asset.hash_,
            mimetype=asset.mime or "application/octet-stream",
            asset_type=asset_type_name,
            required_role=asset.required_role,
            original_filename=asset.original_filename,
            description=asset.description,
            created_at=asset.created_at,
            created_by=asset.created_by,
            updated_at=asset.updated_at,
            updated_by=asset.updated_by,
            data=asset.data,
        )

    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")


@router.patch("/{asset_id}", response_model=AssetMetadata)
async def update_asset(
    asset_id: UUID,
    update: AssetUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """Update asset metadata."""
    try:
        asset = await service.update_asset(
            asset_id=asset_id,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
            description=update.description,
            required_role=update.required_role,
            data=update.data,
        )

        # Get asset type name
        asset_type_obj = await asset.asset_type
        asset_type_name = asset_type_obj.name if asset_type_obj else "unknown"

        return AssetMetadata(
            id=asset.id,
            uri=asset.uri,
            sha256=asset.hash_,
            mimetype=asset.mime or "application/octet-stream",
            asset_type=asset_type_name,
            required_role=asset.required_role,
            original_filename=asset.original_filename,
            description=asset.description,
            created_at=asset.created_at,
            created_by=asset.created_by,
            updated_at=asset.updated_at,
            updated_by=asset.updated_by,
            data=asset.data,
        )

    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """Soft-delete an asset."""
    try:
        await service.delete_asset(
            asset_id=asset_id,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
        )
        return None

    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/", response_model=AssetList)
async def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    created_by: Optional[UUID] = None,
    mimetype: Optional[str] = None,
    search: Optional[str] = None,
    include_deleted: bool = False,
    current_user: CurrentUser = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """List assets with pagination and filtering."""
    query = Asset.all()

    # Filter deleted
    if not include_deleted:
        query = query.filter(deleted_at__isnull=True)
    elif include_deleted and current_user["role"] != "admin":
        # Only admins can see deleted assets
        query = query.filter(deleted_at__isnull=True)

    # Apply filters
    if asset_type:
        asset_type_obj = await AssetType.get_or_none(name=asset_type)
        if asset_type_obj:
            query = query.filter(asset_type_id=asset_type_obj.id)

    if created_by:
        query = query.filter(created_by=created_by)

    if mimetype:
        query = query.filter(mime_id=mimetype)

    if search:
        assets_desc = await Asset.filter(
            deleted_at__isnull=True,
            description__icontains=search,
        ).values_list("id", flat=True)
        assets_fname = await Asset.filter(
            deleted_at__isnull=True,
            original_filename__icontains=search,
        ).values_list("id", flat=True)
        search_ids = list(set(assets_desc) | set(assets_fname))
        query = query.filter(id__in=search_ids)

    # Pagination
    total = await query.count()
    pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    assets = await query.offset(offset).limit(page_size).all()

    # Filter by access control and format response
    accessible_assets = []
    for asset in assets:
        try:
            await service.get_asset_metadata(
                asset_id=asset.id,
                user_id=current_user["user_id"],
                user_role=current_user["role"],
                check_access=True,
            )

            # Get asset type name
            asset_type_obj = await AssetType.get_or_none(id=getattr(asset, "asset_type_id", None))
            asset_type_name = asset_type_obj.name if asset_type_obj else "unknown"

            accessible_assets.append(
                AssetMetadata(
                    id=asset.id,
                    uri=asset.uri,
                    sha256=asset.hash_,
                    mimetype=asset.mime or "application/octet-stream",
                    asset_type=asset_type_name,
                    required_role=asset.required_role,
                    original_filename=asset.original_filename,
                    description=asset.description,
                    created_at=asset.created_at,
                    created_by=asset.created_by,
                    updated_at=asset.updated_at,
                    updated_by=asset.updated_by,
                    data=asset.data,
                )
            )
        except AccessDeniedError:
            pass

    return AssetList(
        items=accessible_assets,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/by-hash/{sha256}", response_model=AssetMetadata)
async def find_by_hash(
    sha256: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """Find asset by SHA256 hash."""
    try:
        asset = await service.get_asset_by_hash(sha256)
        if not asset:
            raise HTTPException(status_code=404, detail="No asset with this SHA256")

        # Check access
        await service.get_asset_metadata(
            asset_id=asset.id,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
            check_access=True,
        )

        # Get asset type name
        asset_type_obj = await asset.asset_type
        asset_type_name = asset_type_obj.name if asset_type_obj else "unknown"

        return AssetMetadata(
            id=asset.id,
            uri=asset.uri,
            sha256=asset.hash_,
            mimetype=asset.mime or "application/octet-stream",
            asset_type=asset_type_name,
            required_role=asset.required_role,
            original_filename=asset.original_filename,
            description=asset.description,
            created_at=asset.created_at,
            created_by=asset.created_by,
            updated_at=asset.updated_at,
            updated_by=asset.updated_by,
            data=asset.data,
        )

    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")


@router.post("/internal/maintenance/cleanup-orphaned", response_model=OrphanedFilesReport)
async def cleanup_orphaned(
    service: AssetService = Depends(get_asset_service),
):
    """Internal endpoint to cleanup orphaned asset metadata."""
    result = await service.cleanup_orphaned_metadata()
    return OrphanedFilesReport(
        scanned=result["scanned"],
        missing_files=result["missing_files"],
        recovered=result["recovered"],
    )
