from datetime import date, datetime

from tortoise import fields
from tortoise.models import Model
from tortoise.signals import pre_save
from tortoise.exceptions import ValidationError

from depot_server.db2.models.common import Condition

class ItemInstance(Model):
    class Meta:
        table: str = "depot_item_instance"

    id = fields.UUIDField(primary_key=True)
    item = fields.ForeignKeyField("depot.Item", on_delete=fields.RESTRICT, null=False, related_name="item_instances")
    purpose = fields.ForeignKeyField("depot.ItemPurpose", on_delete=fields.RESTRICT, null=False, related_name="item_instances")
    external_id = fields.CharField(null=True, max_length=100)
    serial_number = fields.TextField(null=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    #created_by = fields.UUIDField(null=False)
    manufacture_date = fields.DateField(null=False)
    purchase_date = fields.DateField(null=False)
    first_use_date = fields.DateField(null=False)
    condition = fields.CharEnumField(Condition)
    condition_comment = fields.TextField(null=True)
    assets = fields.ManyToManyField("depot.Asset", on_delete=fields.RESTRICT, related_name="item_instances")


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

@pre_save(ItemInstance)
async def validate_item_purpose(sender: type[ItemInstance], instance: ItemInstance, using_db, update_fields) -> None:
    items = await ItemInstance.filter(purpose=instance.purpose).distinct().values_list("item_id", flat=True)
    if len(items) > 1 or (len(items) == 1 and items[0] != instance.item_id):
        raise ValidationError(f"You can not assign different items to the same purpose. Conflicting item IDs: {items}")

@pre_save(ItemInstance)
async def validate_colliding_serial_numbers(sender: type[ItemInstance], instance: ItemInstance, using_db, update_fields) -> None:
    query = ItemInstance.filter(item=instance.item, serial_number=instance.serial_number)
    if instance.id:
        query = query.exclude(id=instance.id)
    existing_instance = await query.first()
    if existing_instance:
        raise ValidationError(f"An item instance with the same item and serial number already exists. Conflicting instance ID: {existing_instance.id}")

@pre_save(ItemInstance)
async def validate_colliding_external_ids(sender: type[ItemInstance], instance: ItemInstance, using_db, update_fields) -> None:
    if instance.external_id is None:
        return
    query = ItemInstance.filter(item=instance.item, external_id=instance.external_id)
    if instance.id:
        query = query.exclude(id=instance.id)
    existing_instance = await query.first()
    if existing_instance:
        raise ValidationError(f"An item instance with the same item and external ID already exists. Conflicting instance ID: {existing_instance.id}")