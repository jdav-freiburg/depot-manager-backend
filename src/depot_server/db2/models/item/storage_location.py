from tortoise import fields
from tortoise.models import Model

from ..asset.asset import Asset

class StorageLocation(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    is_ausgabepflichtig = fields.BooleanField(default=False, null=False)

    map_asset = fields.ForeignKeyField(Asset, on_delete=fields.SET_NULL, null=True)
