from tortoise import fields
from tortoise.models import Model
from tortoise.migrations.constraints import UniqueConstraint

class ItemPurpose(Model):
    class Meta:
        table: str = "depot_item_purpose"

    id = fields.UUIDField(primary_key=True)
    item = fields.ForeignKeyField("depot.Item", related_name="item_purposes")

    # Reverse relations defined in other models
    item_instances: fields.ReverseRelation["ItemInstance"]
    lendable_purpose_link: fields.ReverseRelation["LinkLendablePurpose"]
