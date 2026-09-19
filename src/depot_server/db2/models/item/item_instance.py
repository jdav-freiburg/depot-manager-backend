from datetime import date, datetime

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
    manufacture_date = fields.DateField(null=False)
    purchase_date = fields.DateField(null=False)
    first_use_date = fields.DateField(null=False)
    condition = fields.CharEnumField(Condition)
    condition_comment = fields.TextField(null=True)


    @property
    def is_too_old(self) -> bool:
        return self._is_too_old_at(datetime.now().date())

    def _is_too_old_at(self, date: date) -> bool:
        manufacture_expired = (
            self.item.max_lifespan is not None
            and date - self.manufacture_date > self.item.max_lifespan
        )
        usage_expired = (
            self.item.max_usage_lifespan is not None
            and date - self.first_use_date > self.item.max_usage_lifespan
        )
        return manufacture_expired or usage_expired