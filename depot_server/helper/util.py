import asyncio
import pytz
import datetime
from typing import Any, Annotated

from pydantic.functional_validators import AfterValidator, BeforeValidator


def utc_now() -> datetime.datetime:
    now = datetime.datetime.now(tz=pytz.UTC)
    return now.replace(tzinfo=pytz.UTC, microsecond=now.microsecond // 1000 * 1000)


def set_loop_attr(key: str, data: Any) -> None:
    setattr(asyncio.get_running_loop(), f"_{key}", data)


def get_loop_attr(key: str) -> Any:
    return getattr(asyncio.get_running_loop(), f"_{key}", None)


def truncate_datetimes(dt: datetime.datetime) -> datetime.date:
    match dt:
        case datetime.date():
            return dt
        case datetime.datetime():
            return dt.date()
        case int(_):
            return datetime.datetime.fromordinal(dt).date()
        case _:
            raise ValueError(f"Invlaid date of type {type(dt)}: {dt}")
"""
This is our own date type with custom validation.
Since dates are stored as datetime in the db (time != 0), we get a validation
error with pydantic 2. To work around until we have a db migration, all
models should use this type instead of datetime.date to automatically strip 
time from them
"""
date = Annotated[datetime.date, BeforeValidator(truncate_datetimes)]