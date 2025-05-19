from pydantic import BaseModel as _BaseModel


def camelcase(name: str) -> str:
    name_parts = name.split('_')
    return name_parts[0].lower() + ''.join(part.capitalize() for part in name_parts[1:])


class BaseModel(_BaseModel):
    class Config:
        populate_by_name = True

        alias_generator = camelcase
