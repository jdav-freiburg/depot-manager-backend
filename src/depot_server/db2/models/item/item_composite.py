from tortoise import fields
from tortoise.models import Model


class ItemComposite(Model):
    class Meta:
        table: str = "depot_item_composite"
    id = fields.UUIDField(primary_key=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)
    lendable = fields.BooleanField(description="Shows if the item can actually be lent or not. ")


class ItemCompositeLink(Model):
    class Meta:
        table: str = "depot_link_item_composite__item"

    id = fields.UUIDField(primary_key=True)

    item_composite = fields.ForeignKeyField("depot.ItemComposite", null=False, related_name="item_composite_link")
    item = fields.ForeignKeyField("depot.Item", null=False, related_name="item_link")

    amount = fields.IntField(null=False, description="The quantity of the item in the composite")