from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class ItemCompositeBase(BaseModel):
    name: str
    description: Optional[str] = None
    lendable: bool
    elements: dict[UUID, int] = {}  # Mapping of item_id to amount of items in the composite

class ItemComposite(ItemCompositeBase):
    id: UUID
