from tortoise import fields
from tortoise.models import Model

class ItemPurpose(Model):
    class Meta:
        table: str = "depot_item_purpose"

    id = fields.UUIDField(primary_key=True)
    description = fields.TextField(null=False)

    # Reverse relations defined in other models
    item_instances: fields.ReverseRelation["ItemInstance"]
    lendable_purpose_link: fields.ReverseRelation["LinkLendablePurpose"]
