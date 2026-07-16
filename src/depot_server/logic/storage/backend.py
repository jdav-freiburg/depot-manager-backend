from abc import ABC, abstractmethod
from typing import AsyncIterator


class StorageBackend(ABC):
    """Abstract base for storage implementations."""

    @abstractmethod
    async def write(self, path: str, content: bytes) -> None:
        """Write file to storage."""
        pass

    @abstractmethod
    async def read(self, path: str) -> bytes:
        """Read file from storage."""
        pass

    @abstractmethod
    async def read_stream(self, path: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        """Read file as async byte stream for large files."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass


class LocalFilesystemBackend(StorageBackend):
    """Store files on local filesystem."""

    def __init__(self, base_path: str):
        import os
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        """Convert asset path to filesystem path, removing file:// prefix."""
        import os
        if path.startswith("file://"):
            path = path[7:]
        full_path = os.path.join(self.base_path, path.lstrip("/"))
        return full_path

    async def write(self, path: str, content: bytes) -> None:
        import aiofiles
        import os
        full_path = self._resolve_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)

    async def read(self, path: str) -> bytes:
        import aiofiles
        full_path = self._resolve_path(path)
        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def read_stream(self, path: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        import aiofiles
        full_path = self._resolve_path(path)
        async with aiofiles.open(full_path, "rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    async def delete(self, path: str) -> None:
        import os
        full_path = self._resolve_path(path)
        if os.path.exists(full_path):
            os.remove(full_path)

    async def exists(self, path: str) -> bool:
        import os
        full_path = self._resolve_path(path)
        return os.path.exists(full_path)


class S3Backend(StorageBackend):
    """Store files on AWS S3."""

    def __init__(self, bucket: str, region: str):
        self.bucket = bucket
        self.region = region
        self._client = None

    async def _get_client(self):
        """Lazy-load S3 client."""
        if self._client is None:
            import aioboto3  # type: ignore[import-untyped]
            session = aioboto3.Session()
            self._client = session.client("s3", region_name=self.region)
        return self._client

    def _resolve_path(self, path: str) -> str:
        """Convert asset path to S3 key, removing s3:// prefix."""
        if path.startswith("s3://"):
            path = path[5:]
            path = path.split("/", 1)[1] if "/" in path else path
        return path.lstrip("/")

    async def write(self, path: str, content: bytes) -> None:
        async with await self._get_client() as client:
            key = self._resolve_path(path)
            await client.put_object(Bucket=self.bucket, Key=key, Body=content)

    async def read(self, path: str) -> bytes:
        async with await self._get_client() as client:
            key = self._resolve_path(path)
            response = await client.get_object(Bucket=self.bucket, Key=key)
            return await response["Body"].read()

    async def read_stream(self, path: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        async with await self._get_client() as client:
            key = self._resolve_path(path)
            response = await client.get_object(Bucket=self.bucket, Key=key)
            body = response["Body"]
            while True:
                chunk = await body.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    async def delete(self, path: str) -> None:
        async with await self._get_client() as client:
            key = self._resolve_path(path)
            await client.delete_object(Bucket=self.bucket, Key=key)

    async def exists(self, path: str) -> bool:
        async with await self._get_client() as client:
            key = self._resolve_path(path)
            try:
                await client.head_object(Bucket=self.bucket, Key=key)
                return True
            except Exception:
                return False


class ExternalURLBackend(StorageBackend):
    """Handle external URLs (no actual storage, links only)."""

    async def write(self, path: str, content: bytes) -> None:
        raise NotImplementedError("External URL backend does not support write operations")

    async def read(self, path: str) -> bytes:
        raise NotImplementedError("External URL backend does not support read operations")

    async def read_stream(self, path: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        raise NotImplementedError("External URL backend does not support read operations")

    async def delete(self, path: str) -> None:
        # External URLs are not deleted, just the reference is removed
        pass

    async def exists(self, path: str) -> bool:
        # External URLs are assumed to exist (trusted admin input)
        return True
