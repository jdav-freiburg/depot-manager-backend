from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StorageLocationPending(BaseModel):
    name: str
    description: str
    map_item: Optional[UUID] = None
    is_subject_to_issuance: bool = Field(default=False)


class StorageLocation(StorageLocationPending):
    id: UUID
