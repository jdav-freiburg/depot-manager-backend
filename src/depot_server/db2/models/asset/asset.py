from tortoise import fields
from tortoise.models import Model

from .asset_type import AssetType
from .mime_type import AllowedMimeType


class Asset(Model):
    class Meta:
        table: str = "depot_asset"

    id = fields.UUIDField(primary_key=True, unique=True)

    # RESTRICT -> When trying to delete the mimetype of this Asset, it won't be allowed. Deleting the mimetype
    # will only be possible when no asset uses it
    mime = fields.ForeignKeyField(to=AllowedMimeType, on_delete=fields.RESTRICT, null=False,
                                  description="The mime type of the asset", related_name="assets")

    asset_type = fields.ForeignKeyField(to=AssetType, on_delete=fields.RESTRICT, null=False,
                                        description="The type of the asset", related_name="assets")

    created_by = fields.UUIDField(null=False, description="The user id who created the asset")
    created_at = fields.DatetimeField(null=False, description="The timestamp when the asset was created")
    updated_by = fields.UUIDField(null=False, description="The user id who updated the asset")
    updated_at = fields.DatetimeField(null=False, description="The timestamp when the asset was last updated")

    uri = fields.TextField(null=False, description="The URI of the asset (file://, s3://, or https://)")
    hash_ = fields.TextField(null=False, description="The sha256 hash of the asset content")
    description = fields.TextField(null=True, description="Human-readable description of the asset")
    original_filename = fields.TextField(null=True, description="Original filename as uploaded")

    required_role = fields.CharField(max_length=20, null=False, default="user",
                                     description="Minimum role required to access (user, manager, admin)")

    data = fields.JSONField(null=True, description="Free-form key-value metadata")

    deleted_at = fields.DatetimeField(null=True, description="Soft-delete timestamp (NULL = active)")
    error_status = fields.TextField(null=True, description="Error state: UPLOAD_FAILED, FILE_MISSING, CORRUPT_FILE")
