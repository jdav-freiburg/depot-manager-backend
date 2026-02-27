from enum import StrEnum

from tortoise import fields
from tortoise.models import Model

from .item import Item

class ReservationType(StrEnum):
    TEAM = 'team'
    PRIVATE = 'private'

class ReservationState(StrEnum):
    RESERVED = 'reserved'
    INVENTUR = 'inventur'
    MAINTENANCE = 'maintenance'

class Reservation(Model):
    id = fields.UUIDField(pk=True)
    name = fields.data.TextField()
    start = fields.DatetimeField(null=False)
    end = fields.DatetimeField(null=False)

    user = fields.UUIDField(null=False)
    team = fields.UUIDField(null=True)
    contact = fields.data.TextField()
    is_active = fields.BooleanField()
    reservation_type = fields.CharEnumField(ReservationType, null=False)
    reservation_state = fields.CharEnumField(ReservationState, null=False, default=ReservationState.RESERVED)

class ReservationLink(Model):
    id = fields.UUIDField(pk=True)

    reservation = fields.ForeignKeyField(Reservation, null=False, related_name="reservation_id")
    item = fields.ForeignKeyField(Item, null=False, related_name="item_id")

    borrowed = fields.DatetimeField(null=True)
    borrowed_message = fields.data.TextField(null=True)
    returned = fields.DatetimeField(null=True)
    returned_message = fields.data.TextField(null=True)
    collector = fields.TextField(description="The person who picked up the item")
