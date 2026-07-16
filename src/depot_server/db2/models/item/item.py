from datetime import datetime

from tortoise import fields
from tortoise.models import Model

from depot_server.db2.models.asset.asset import Asset
from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item_group import ItemGroup
from depot_server.db2.models.item.storage_location import StorageLocation
from depot_server.db2.models.report.report_profile import ReportProfile
from .reservation import Reservation
from .tag import Tag


class Item(Model):
    class Meta:
        table: str = "depot_item"

    id = fields.UUIDField(primary_key=True)

    report_profile = fields.ForeignKeyField(ReportProfile, on_delete=fields.RESTRICT, null=True, related_name="items")
    group = fields.ForeignKeyField(ItemGroup, on_delete=fields.RESTRICT, null=False, related_name="items")
    storage_location = fields.ForeignKeyField(StorageLocation, on_delete=fields.RESTRICT, null=True,
                                              related_name="items")
    assets = fields.ManyToManyField(Asset, on_delete=fields.RESTRICT, related_name="items")
    tags = fields.ManyToManyField(Tag, null=True, on_delete=fields.SET_NULL, related_name="items")
    reservations = fields.ManyToManyField(
        Reservation,
        through="models.item.reservation.ReservationLink",
        forward_key="reservation_id",
        backward_key="item_id",
        related_name="items"
    )

    external_id = fields.CharField(unique=True, null=False, max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField(null=False)
    name = fields.data.TextField(null=False)
    description = fields.data.TextField(null=True)
    manufacturer = fields.data.TextField(null=True)
    model = fields.data.TextField(null=True)
    serial_number = fields.data.TextField(null=True)
    manufacture_date = fields.DatetimeField(null=True)
    purchase_date = fields.DatetimeField(null=True)
    first_use_date = fields.DatetimeField(null=True)
    lendable = fields.BooleanField(description="Shows if the item can actually be lent or not. "
                                               "Useful for items that are registered for documentation purposes only")
    condition = fields.CharEnumField(Condition)

    @property
    def last_inspection(self) -> datetime:
        """
        Fetches the date of the last inspection of this item
        """
        raise NotImplementedError
