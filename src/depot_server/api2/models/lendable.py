from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class APILendableBase(BaseModel):
    name: str
    description: Optional[str] = None
    storage_location: UUID
    ausgabepflichtig: bool
    items: dict[UUID, int]  # item_id -> quantity

class APICreateLendable(APILendableBase):
    parent: Optional[UUID] = None  # UUID of the parent lendable group if it exists

class APIUpdateLendable(APILendableBase):
    in_limbus: Optional[int] = None

class APILendable(APILendableBase):
    id: UUID
    in_limbus: int
