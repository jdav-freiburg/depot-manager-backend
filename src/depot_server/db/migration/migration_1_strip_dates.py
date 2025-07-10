from uuid import uuid4

import motor.motor_asyncio
import random
from datetime import date

from depot_server.config import config
from depot_server.db.model import DbReservation

__description__ = "Strip all hours, minutes, ... from datetimes to satisfy new pydantic requirements for the `date` datatype"


async def migrate(db: motor.motor_asyncio.AsyncIOMotorDatabase):
    """
    go through each model containing datetime.date fields and set all
    values to zero which aren't year, month or day
    """
    async for reservation  in db['reservation'].find({}):
        raise NotImplementedError("Strip all times from datetimes")

async def demigrate(db: motor.motor_asyncio.AsyncIOMotorDatabase):
        raise NotImplementedError("find out what to do here")

