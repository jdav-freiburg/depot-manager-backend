from datetime import datetime
from enum import StrEnum

from tortoise import fields
from tortoise.models import Model

from depot_server.db2.models.asset.asset import Asset
from depot_server.db2.models.item.item_group import ItemGroup
from depot_server.db2.models.item.storage_location import StorageLocation
from depot_server.db2.models.report.report_profile import ReportProfile
from .reservation import Reservation
from .tag import Tag


class PsaCategory(StrEnum):
    NONE = 'none'
    CAT_1 = "cat_1"
    CAT_2 = "cat_2"
    CAT_3 = "cat_3"


class Item(Model):
    class Meta:
        table: str = "depot_item"

    id = fields.UUIDField(primary_key=True)
    group = fields.OneToOneField(ItemGroup, source_field="group_id", to_field="id", on_delete=fields.RESTRICT,
                                 related_name="item")
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)
    manufacturer = fields.TextField(null=True)
    model = fields.TextField(null=True)
    report_profile = fields.ForeignKeyField(ReportProfile, on_delete=fields.RESTRICT, null=True, related_name="items")
    max_lifespan = fields.TimeDeltaField(null=True, description="The maximum lifespan. Formated in ISO 8601 duration format(e.g., P1Y2M3D). Find it in the GAL")
    max_usage_lifespan = fields.TimeDeltaField(null=True, description="The maximum lifespan of the item if it is used regularly. Formated in ISO 8601 duration format(e.g., P1Y2M3D)Find it in the GAL")
    psa_category = fields.CharEnumField(PsaCategory, null=False)

    storage_location = fields.ForeignKeyField(StorageLocation, on_delete=fields.RESTRICT, null=True,
                                              related_name="items")
    assets = fields.ManyToManyField(Asset, on_delete=fields.RESTRICT, related_name="items")
    created_at = fields.DatetimeField(auto_now_add=True)
    #tags = fields.ManyToManyField(Tag, null=True, on_delete=fields.SET_NULL, related_name="items")
    # reservations = fields.ManyToManyField(
    #     Reservation,
    #     through="models.item.reservation.ReservationLink",
    #     forward_key="reservation_id",
    #     backward_key="item_id",
    #     related_name="items"
    # )


    #created_by = fields.UUIDField(null=False)

