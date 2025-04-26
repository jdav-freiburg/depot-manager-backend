from typing import Optional, List

from .base import BaseModel


class User(BaseModel):
    sub: str
    name: str
    email: str
    picture: Optional[str] = None
    phone_number: Optional[str] = None
    roles: Optional[List[str]] = None
    teams: Optional[List[str]] = None
