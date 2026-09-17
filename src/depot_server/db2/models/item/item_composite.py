from tortoise import fields
from tortoise.models import Model
from tortoise.validators import MinValueValidator


class ItemComposite(Model):
    class Meta:
        table: str = "depot_item_composite"
    id = fields.UUIDField(primary_key=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)
    in_limbus = fields.IntField(null=False, default=0, validators=[MinValueValidator(0)],
                                description="The amount of this items where it is unsure if they are lost or if they return.")
    lendable = fields.BooleanField(description="Shows if the item can actually be lent or not. ")


class ItemCompositeLink(Model):
    class Meta:
        table: str = "depot_link_item_composite__item"

    id = fields.UUIDField(primary_key=True)

    item_composite = fields.ForeignKeyField("depot.ItemComposite", null=False, related_name="item_composite_link")
    item = fields.ForeignKeyField("depot.Item", null=False, related_name="item_link")
    amount = fields.IntField(null=False, validators=[MinValueValidator(1)], description="The quantity of the item in the composite")