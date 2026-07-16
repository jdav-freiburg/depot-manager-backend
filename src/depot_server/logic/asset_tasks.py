"""Background tasks for asset maintenance and cleanup."""

from datetime import datetime, timedelta
import logging

from depot_server.db2.models.asset import Asset
from depot_server.logic.storage.factory import StorageFactory

logger = logging.getLogger(__name__)


async def cleanup_expired_soft_deletes(
    storage_factory: StorageFactory,
    retention_days: int = 30,
) -> dict:
    """
    Hard-delete assets that have been soft-deleted for retention_days.

    This task is designed to run on a schedule (e.g., daily at 2 AM).
    Can be integrated with Celery or run directly.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    expired = await Asset.filter(deleted_at__lt=cutoff_date).all()

    deleted_count = 0
    failed_count = 0
    failed_ids = []

    for asset in expired:
        try:
            # Try to delete file from storage
            backend = storage_factory.get_backend_for_uri(asset.uri)
            path = storage_factory.get_path_from_uri(asset.uri)
            await backend.delete(path)
        except Exception as e:
            logger.warning(f"Failed to delete file for asset {asset.id}: {e}")
            failed_count += 1
            failed_ids.append(str(asset.id))
            continue

        try:
            await asset.delete()
            deleted_count += 1
            logger.info(f"Hard-deleted asset {asset.id}")
        except Exception as e:
            logger.error(f"Failed to delete asset record {asset.id}: {e}")
            failed_count += 1

    result = {
        "deleted": deleted_count,
        "failed": failed_count,
        "failed_ids": failed_ids,
        "cutoff_date": cutoff_date.isoformat(),
    }
    logger.info(f"Cleanup task completed: {result}")
    return result


async def cleanup_orphaned_metadata(
    storage_factory: StorageFactory,
) -> dict:
    """
    Find and report orphaned asset metadata (error_status set).

    Checks if files exist in storage:
    - If missing: marks as FILE_MISSING
    - If exists: clears error_status
    - Can optionally delete metadata if instructed
    """
    orphaned = await Asset.filter(error_status__isnull=False).all()

    missing = []
    recovered = []
    scanned = len(orphaned)

    for asset in orphaned:
        try:
            backend = storage_factory.get_backend_for_uri(asset.uri)
            path = storage_factory.get_path_from_uri(asset.uri)
            exists = await backend.exists(path)

            if not exists:
                asset.error_status = "FILE_MISSING"
                await asset.save()
                missing.append({
                    "asset_id": str(asset.id),
                    "uri": asset.uri,
                    "error_status": asset.error_status,
                })
                logger.warning(f"Asset {asset.id} has missing file")
            else:
                # File exists, clear error status
                asset.error_status = ""  # type: ignore[assignment]
                await asset.save()
                recovered.append(str(asset.id))
                logger.info(f"Recovered asset {asset.id}")
        except Exception as e:
            logger.error(f"Error checking asset {asset.id}: {e}")
            pass

    result = {
        "scanned": scanned,
        "missing_files": missing,
        "recovered": len(recovered),
        "recovered_ids": recovered,
    }
    logger.info(f"Orphaned metadata cleanup: {result}")
    return result


# Celery task registration (for when Celery is set up)
# from celery import Celery
# celery_app = Celery('depot_server')
#
# @celery_app.task(name='asset.cleanup_expired')
# def celery_cleanup_expired(retention_days: int = 30):
#     """Celery task wrapper for cleanup_expired_soft_deletes."""
#     from depot_server.config import config
#     from depot_server.logic.storage.factory import StorageFactory
#
#     storage_factory = StorageFactory(
#         local_path=getattr(config, 'storage_local_path', './assets'),
#         s3_bucket=getattr(config, 's3_bucket', ''),
#         s3_region=getattr(config, 's3_region', 'eu-central-1'),
#     )
#     return asyncio.run(cleanup_expired_soft_deletes(storage_factory, retention_days))
#
# @celery_app.task(name='asset.cleanup_orphaned')
# def celery_cleanup_orphaned():
#     """Celery task wrapper for cleanup_orphaned_metadata."""
#     from depot_server.config import config
#     from depot_server.logic.storage.factory import StorageFactory
#
#     storage_factory = StorageFactory(
#         local_path=getattr(config, 'storage_local_path', './assets'),
#         s3_bucket=getattr(config, 's3_bucket', ''),
#         s3_region=getattr(config, 's3_region', 'eu-central-1'),
#     )
#     return asyncio.run(cleanup_orphaned_metadata(storage_factory))
