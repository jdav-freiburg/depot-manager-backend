from tortoise import fields
from tortoise.models import Model

class ItemPurpose(Model):
    class Meta:
        table: str = "depot_item_purpose"

    id = fields.UUIDField(primary_key=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)