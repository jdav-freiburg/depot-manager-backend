from datetime import datetime

from tortoise import fields
from tortoise.models import Model

from depot_server.db2.models.common import Condition
from depot_server.db2.models.item.item import Item

class ItemInstance(Model):
    class Meta:
        table: str = "depot_item_instance"

    id = fields.UUIDField(primary_key=True)
    item = fields.ForeignKeyField(Item, on_delete=fields.RESTRICT, null=False, related_name="item_instances")
    external_id = fields.CharField(null=True, max_length=100)
    serial_number = fields.TextField(null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    #created_by = fields.UUIDField(null=False)
    manufacture_date = fields.DatetimeField(null=False)
    purchase_date = fields.DatetimeField(null=False)
    first_use_date = fields.DatetimeField(null=False)
    condition = fields.CharEnumField(Condition)
    condition_comment = fields.TextField(null=True)


    @property
    def last_inspection(self) -> datetime:
        """
        Fetches the date of the last inspection of this item instance
        """
        raise NotImplementedError

    @property
    def is_too_old(self) -> bool:
        """
        Checks if the item instance is too old to be used
        """
        raise NotImplementedError