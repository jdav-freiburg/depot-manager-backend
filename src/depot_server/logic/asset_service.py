import hashlib
from datetime import datetime
from typing import Optional, AsyncIterator
from uuid import UUID, uuid4

from fastapi import UploadFile

from depot_server.db2.models.asset import Asset, AllowedMimeType, AssetType
from depot_server.db2.repository.asset import AssetRepo
from depot_server.logic.storage.factory import StorageFactory


class AssetNotFoundError(Exception):
    """Asset not found or is soft-deleted."""
    pass


class AccessDeniedError(Exception):
    """User lacks required role to access asset."""
    pass


class FileTooLargeError(Exception):
    """File exceeds size limit."""
    pass


class MimetypeNotAllowedError(Exception):
    """MIME type not in whitelist."""
    pass


class DuplicateFileError(Exception):
    """File with same content already exists."""
    pass


class StorageBackendError(Exception):
    """Storage backend failure."""
    pass


class AssetService:
    """Service for managing assets with access control, deduplication, and storage abstraction."""

    ROLE_HIERARCHY = {"user": 0x01, "manager": 0x02, "admin": 0x04}
    MAX_FILE_SIZE_MB = 100

    def __init__(self, storage_factory: StorageFactory):
        self.storage = storage_factory

    async def _calculate_sha256(self, content: bytes) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    async def _check_access(self, user_role: str, asset: Asset) -> bool:
        """Check if user has required role to access asset."""
        user_role_val = self.ROLE_HIERARCHY.get(user_role, 0)
        asset_role_val = self.ROLE_HIERARCHY.get(asset.required_role, 0x01)
        return user_role_val >= asset_role_val

    async def _check_upload_permission(self, user_role: str) -> None:
        """Verify user can upload assets (manager or admin)."""
        if user_role not in ("manager", "admin"):
            raise AccessDeniedError("Only managers and admins can upload assets")

    async def upload_asset(
        self,
        file: UploadFile,
        asset_type_id: UUID,
        required_role: str,
        user_id: UUID,
        user_role: str,
        description: Optional[str] = None,
    ) -> Asset:
        """Upload and store a file with deduplication and access control."""
        await self._check_upload_permission(user_role)

        # Validate MIME type
        mime = await AllowedMimeType.get_or_none(mime=file.content_type)
        if not mime:
            raise MimetypeNotAllowedError(f"MIME type {file.content_type} not allowed")

        # Check asset type exists
        asset_type = await AssetType.get_or_none(id=asset_type_id)
        if not asset_type:
            raise ValueError(f"Asset type {asset_type_id} not found")

        # Read file content
        content = await file.read()

        # Check file size
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            raise FileTooLargeError(f"File exceeds {self.MAX_FILE_SIZE_MB}MB limit")

        # Calculate SHA256 and check for duplicates
        sha256 = await self._calculate_sha256(content)
        existing = await Asset.get_or_none(hash_=sha256, deleted_at__isnull=True)
        if existing:
            raise DuplicateFileError(f"File with same content already exists: {existing.id}")

        # Generate asset ID and URI
        asset_id = uuid4()
        uri = f"file:///assets/{asset_id}"

        # Try to store file
        try:
            backend = self.storage.get_backend_for_uri(uri)
            await backend.write(uri, content)
        except Exception as e:
            # Create asset record with error status if storage fails
            asset = await Asset.create(
                id=asset_id,
                mime_id=mime.mime,
                asset_type_id=asset_type_id,
                uri=uri,
                hash_=sha256,
                required_role=required_role,
                created_by=user_id,
                created_at=datetime.utcnow(),
                updated_by=user_id,
                updated_at=datetime.utcnow(),
                description=description,
                original_filename=file.filename,
                error_status="UPLOAD_FAILED",
            )
            raise StorageBackendError(f"Failed to store file: {str(e)}")

        # Create asset record
        asset = await Asset.create(
            id=asset_id,
            mime_id=mime.mime,
            asset_type_id=asset_type_id,
            uri=uri,
            hash_=sha256,
            required_role=required_role,
            created_by=user_id,
            created_at=datetime.utcnow(),
            updated_by=user_id,
            updated_at=datetime.utcnow(),
            description=description,
            original_filename=file.filename,
        )

        return asset

    async def get_asset_bytes(
        self,
        asset_id: UUID,
        user_id: UUID,
        user_role: str,
        check_access: bool = True,
    ) -> bytes:
        """Get asset content as bytes. Suitable for small files."""
        asset = await Asset.get_or_none(id=asset_id, deleted_at__isnull=True)
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")

        if check_access:
            has_access = await self._check_access(user_role, asset)
            if not has_access:
                raise AccessDeniedError("User lacks required role")

        if asset.error_status == "FILE_MISSING":
            raise FileNotFoundError("File missing from storage")

        try:
            backend = self.storage.get_backend_for_uri(asset.uri)
            path = self.storage.get_path_from_uri(asset.uri)
            return await backend.read(path)
        except FileNotFoundError:
            asset.error_status = "FILE_MISSING"
            await asset.save()
            raise FileNotFoundError("File missing from storage")

    async def get_asset_stream(
        self,
        asset_id: UUID,
        user_id: UUID,
        user_role: str,
        check_access: bool = True,
        chunk_size: int = 8192,
    ) -> AsyncIterator[bytes]:
        """Get asset as async byte stream. Suitable for large files."""
        asset = await Asset.get_or_none(id=asset_id, deleted_at__isnull=True)
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")

        if check_access:
            has_access = await self._check_access(user_role, asset)
            if not has_access:
                raise AccessDeniedError("User lacks required role")

        if asset.error_status == "FILE_MISSING":
            raise FileNotFoundError("File missing from storage")

        try:
            backend = self.storage.get_backend_for_uri(asset.uri)
            path = self.storage.get_path_from_uri(asset.uri)
            async for chunk in await backend.read_stream(path, chunk_size):
                yield chunk
        except FileNotFoundError:
            asset.error_status = "FILE_MISSING"
            await asset.save()
            raise FileNotFoundError("File missing from storage")

    async def get_asset_metadata(
        self,
        asset_id: UUID,
        user_id: Optional[UUID] = None,
        user_role: Optional[str] = None,
        check_access: bool = True,
    ) -> Asset:
        """Get asset metadata without file content."""
        asset = await Asset.get_or_none(id=asset_id, deleted_at__isnull=True)
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")

        if check_access and user_role:
            has_access = await self._check_access(user_role, asset)
            if not has_access:
                raise AccessDeniedError("User lacks required role")

        return asset

    async def get_asset_by_hash(self, sha256: str) -> Optional[Asset]:
        """Find asset by SHA256 hash."""
        return await Asset.get_or_none(hash_=sha256, deleted_at__isnull=True)

    async def update_asset(
        self,
        asset_id: UUID,
        user_id: UUID,
        user_role: str,
        description: Optional[str] = None,
        required_role: Optional[str] = None,
        data: Optional[dict] = None,
    ) -> Asset:
        """Update asset metadata."""
        asset = await Asset.get_or_none(id=asset_id, deleted_at__isnull=True)
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")

        # Only creator or admin can modify
        if asset.created_by != user_id and user_role != "admin":
            raise AccessDeniedError("Only creator or admin can modify this asset")

        if description is not None:
            asset.description = description
        if required_role is not None:
            if required_role not in self.ROLE_HIERARCHY:
                raise ValueError(f"Invalid role: {required_role}")
            asset.required_role = required_role
        if data is not None:
            asset.data = data

        asset.updated_at = datetime.utcnow()
        asset.updated_by = user_id
        await asset.save()

        return asset

    async def delete_asset(
        self,
        asset_id: UUID,
        user_id: UUID,
        user_role: str,
        hard_delete: bool = False,
    ) -> None:
        """Soft-delete or hard-delete an asset."""
        asset = await Asset.get_or_none(id=asset_id)
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")

        # Only creator or admin can delete
        if asset.created_by != user_id and user_role != "admin":
            raise AccessDeniedError("Only creator or admin can delete this asset")

        if hard_delete:
            # Only admin can hard-delete
            if user_role != "admin":
                raise AccessDeniedError("Only admin can hard-delete assets")
            # Delete file from storage
            try:
                backend = self.storage.get_backend_for_uri(asset.uri)
                path = self.storage.get_path_from_uri(asset.uri)
                await backend.delete(path)
            except Exception as e:
                # Log but don't fail if file deletion fails
                pass
            # Delete from database
            await asset.delete()
        else:
            # Soft delete
            asset.deleted_at = datetime.utcnow()
            await asset.save()

    async def get_assets_by_item(
        self,
        item_id: UUID,
        user_role: str,
        asset_type_id: Optional[UUID] = None,
    ) -> list[Asset]:
        """Get all assets linked to an item that user can access."""
        # Query assets linked to item
        query = Asset.filter(
            items__id=item_id,
            deleted_at__isnull=True,
        )
        if asset_type_id:
            query = query.filter(asset_type_id=asset_type_id)

        assets = await query.all()

        # Filter by access control
        accessible = []
        for asset in assets:
            if await self._check_access(user_role, asset):
                accessible.append(asset)

        return accessible

    async def cleanup_expired_soft_deletes(self, retention_days: int = 30) -> dict:
        """Hard-delete assets that have been soft-deleted for retention_days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        expired = await Asset.filter(deleted_at__lt=cutoff_date).all()

        deleted_count = 0
        failed_count = 0

        for asset in expired:
            try:
                # Try to delete file from storage
                backend = self.storage.get_backend_for_uri(asset.uri)
                path = self.storage.get_path_from_uri(asset.uri)
                await backend.delete(path)
            except Exception:
                failed_count += 1
                continue

            try:
                await asset.delete()
                deleted_count += 1
            except Exception:
                failed_count += 1

        return {
            "deleted": deleted_count,
            "failed": failed_count,
            "cutoff_date": cutoff_date.isoformat(),
        }

    async def cleanup_orphaned_metadata(self) -> dict:
        """Find and report orphaned asset metadata."""
        orphaned = await Asset.filter(error_status__isnull=False).all()

        missing = []
        recoverable = []

        for asset in orphaned:
            try:
                backend = self.storage.get_backend_for_uri(asset.uri)
                path = self.storage.get_path_from_uri(asset.uri)
                exists = await backend.exists(path)

                if not exists:
                    missing.append({"asset_id": str(asset.id), "uri": asset.uri})
                else:
                    # File exists, clear error status
                    asset.error_status = ""  # type: ignore[assignment]
                    await asset.save()
                    recoverable.append(str(asset.id))
            except Exception:
                pass

        return {
            "scanned": len(orphaned),
            "missing_files": missing,
            "recovered": len(recoverable),
        }
