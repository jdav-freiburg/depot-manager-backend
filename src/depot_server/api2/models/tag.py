import re
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

_HEX_COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")


class TagPending(BaseModel):
    name: str
    description: str
    color: str = Field(..., description="HTML hex color like #rrggbb")


class Tag(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    color: str = Field(..., description="HTML hex color like #rrggbb")

    @field_validator("color", mode="before")
    def _validate_and_normalize_color(cls, v):
        if v is None:
            raise ValueError("color is required")
        s = str(v).strip().lower()
        if not _HEX_COLOR_RE.fullmatch(s):
            raise ValueError("color must be a 6-digit hex code, e.g. #ff0000")
        return s
