from enum import StrEnum

from tortoise import fields
from tortoise.models import Model

from ..common import ReservationImportance, ReservationType


class Reservation(Model):
    class Meta:
        table: str = "depot_reservation"

    id = fields.UUIDField(primary_key=True)

    name = fields.TextField()
    start = fields.DatetimeField(null=False)
    end = fields.DatetimeField(null=False)
    user = fields.UUIDField(null=False)
    team = fields.UUIDField(null=True)
    contact = fields.TextField()
    user_notes = fields.TextField(null=True)
    #is_active = fields.BooleanField()
    reservation_importance = fields.CharEnumField(ReservationImportance, null=False)
    reservation_type = fields.CharEnumField(ReservationType, null=False, default=ReservationType.BORROW)



class ReservationLinkBase(Model):
    class Meta:
        abstract = True

    id = fields.UUIDField(primary_key=True)
    amount = fields.IntField(null=False)
    borrowed = fields.DatetimeField(null=True)
    borrowed_message = fields.TextField(null=True)
    returned = fields.DatetimeField(null=True)
    returned_message = fields.TextField(null=True)
    collector = fields.TextField(description="The person who picked up the item", null=True)


class ReservationItemLink(ReservationLinkBase):
    class Meta:
        table: str = "depot_link_reservation__item"

    item = fields.ForeignKeyField("depot.Item", null=False, related_name="reservation_items")
    reservation = fields.ForeignKeyField("depot.Reservation", null=False, related_name="reservation_items")


class ReservationCompositeLink(ReservationLinkBase):
    class Meta:
        table: str = "depot_link_reservation__composite_item"

    composite_item = fields.ForeignKeyField("depot.ItemComposite", null=False, related_name="composite_item")
    reservation = fields.ForeignKeyField("depot.Reservation", null=False, related_name="reservation_composites")
