from typing import Dict, Optional
from .backend import StorageBackend, LocalFilesystemBackend, S3Backend, ExternalURLBackend


class StorageFactory:
    """Factory for creating and managing storage backends based on URI scheme."""

    def __init__(self, local_path: str, s3_bucket: str, s3_region: str):
        self.backends: Dict[str, StorageBackend] = {
            "file": LocalFilesystemBackend(local_path),
            "s3": S3Backend(s3_bucket, s3_region),
            "https": ExternalURLBackend(),
            "http": ExternalURLBackend(),
            "nc": ExternalURLBackend(),  # Nextcloud
        }

    def get_backend_for_uri(self, uri: str) -> StorageBackend:
        """Route URI to appropriate storage backend."""
        scheme = uri.split("://")[0]
        backend = self.backends.get(scheme)
        if not backend:
            raise ValueError(f"Unknown storage scheme: {scheme}")
        return backend

    def get_path_from_uri(self, uri: str) -> str:
        """Extract path component from URI."""
        scheme = uri.split("://")[0]
        if scheme in ("https", "http", "nc"):
            return uri  # Full URL is the path for external URLs
        parts = uri.split("://", 1)
        if len(parts) > 1:
            return parts[1]
        return uri
