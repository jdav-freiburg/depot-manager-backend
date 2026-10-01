from enum import StrEnum

from tortoise import fields
from tortoise.models import Model
from tortoise.validators import MinValueValidator
from tortoise.migrations.constraints import CheckConstraint

from ..common import ReservationImportance, ReservationType


class Reservation(Model):
    class Meta:
        table: str = "depot_reservation"

    id = fields.UUIDField(primary_key=True)

    name = fields.TextField()
    start = fields.DateField(null=False)
    end = fields.DateField(null=False)
    user = fields.UUIDField(null=False)
    team = fields.UUIDField(null=True)
    contact = fields.TextField()
    user_notes = fields.TextField(null=True)
    collector = fields.TextField(description="The person who picked up the item", null=True)
    reservation_importance = fields.CharEnumField(ReservationImportance, null=False)
    reservation_type = fields.CharEnumField(ReservationType, null=False, default=ReservationType.BORROW)

    reservation_lendable_links: fields.ReverseRelation["LinkReservationLendable"]

class LinkReservationLendable(Model):
    class Meta:
        table: str = "depot_link_reservation__lendable"
        constraints = [
            CheckConstraint("amount > 0", name="check_amount_positive")
        ]

    id = fields.UUIDField(primary_key=True)
    amount = fields.IntField(null=False, validators=[MinValueValidator(0)], description="How many of the lendable are reserved. At pickup this should be updated to the number of lendables that are actually taken by the user.")
    missing_amount = fields.IntField(null=True, validators=[MinValueValidator(0)], description="The amount of lendables that were not there despite the system claiming they were available. This should be updated at pickup.")
    returned_amount = fields.IntField(null=True, validators=[MinValueValidator(0)], description="The amount of lendables that were returned by the user. This should be updated at return.")
    borrowed = fields.DateField(null=True)
    borrowed_message = fields.TextField(null=True)
    returned = fields.DateField(null=True)
    returned_message = fields.TextField(null=True)
    lendable = fields.ForeignKeyField("depot.Lendable", null=False, on_delete=fields.RESTRICT, related_name="reservation_lendable_links")
    reservation = fields.ForeignKeyField("depot.Reservation", null=False, related_name="reservation_lendable_links")


class LinkReservationLinkItemInstance(Model):
    class Meta:
        table: str = "depot_link_reservation__item_instance"
        description = "This table links reservations to specific item instances. This table should be filled at pickup if we want to track which specific item instance was given to the user." \
        " e.g. the user reserved an arbitrary LVS lendable. He then gets the one with numer 5."

    id = fields.UUIDField(primary_key=True)
    link_reservation_lendable = fields.ForeignKeyField("depot.LinkReservationLendable", null=False, related_name="reservation_item_instance_links")
    item_instance = fields.ForeignKeyField("depot.ItemInstance", null=False, on_delete=fields.RESTRICT, related_name="reservation_item_instance_links")