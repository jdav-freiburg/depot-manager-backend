from uuid import UUID, uuid4
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, StringConstraints


HexColor = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        pattern=r"^#[0-9a-fA-F]{6}$",
    ),
]


class APITagPending(BaseModel):
    name: str
    description: str
    color: HexColor = Field(..., description="HTML hex color like #rrggbb")


class APITag(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    color: HexColor = Field(..., description="HTML hex color like #rrggbb")
