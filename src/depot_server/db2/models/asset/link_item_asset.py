from tortoise import fields
from tortoise.models import Model


class LinkItemAsset(Model):
    """
    Link table for Item-Asset relationships.
    Allows items to be associated with multiple assets and vice versa.
    """

    class Meta:
        table: str = "link_item__asset"

    id = fields.UUIDField(primary_key=True)
    item_id = fields.UUIDField(null=False, description="FK to item table")
    asset_id = fields.UUIDField(null=False, description="FK to asset table")

    class PydanticModel:
        exclude = ["id"]
