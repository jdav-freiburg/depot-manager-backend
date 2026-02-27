from tortoise import fields
from tortoise.models import Model

from ..asset.asset import Asset


class StorageLocation(Model):
    class Meta:
        table: str = "depot_storage_location"

    id = fields.UUIDField(pk=True)

    map_asset = fields.ForeignKeyField(Asset, on_delete=fields.SET_NULL, null=True, related_name="locations")

    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    is_ausgabepflichtig = fields.BooleanField(default=False, null=False)
