from tortoise import fields
from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    """Add extended fields to Asset model for access control and soft-delete."""

    depends_on = ("depot", "0003_news")

    operations = [
        ops.AddField(
            model_name="Asset",
            name="required_role",
            field=fields.CharField(
                max_length=20,
                default="user",
                description="Minimum role required to access (user, manager, admin)",
            ),
        ),
        ops.AddField(
            model_name="Asset",
            name="original_filename",
            field=fields.TextField(
                null=True,
                description="Original filename as uploaded",
            ),
        ),
        ops.AddField(
            model_name="Asset",
            name="data",
            field=fields.JSONField(
                null=True,
                description="Free-form key-value metadata",
            ),
        ),
        ops.AddField(
            model_name="Asset",
            name="deleted_at",
            field=fields.DatetimeField(
                null=True,
                description="Soft-delete timestamp (NULL = active)",
            ),
        ),
        ops.AddField(
            model_name="Asset",
            name="error_status",
            field=fields.TextField(
                null=True,
                description="Error state: UPLOAD_FAILED, FILE_MISSING, CORRUPT_FILE",
            ),
        ),
        ops.CreateModel(
            name="LinkItemAsset",
            fields=[
                ("id", fields.UUIDField(primary_key=True, unique=True, db_index=True)),
                ("item_id", fields.UUIDField(description="FK to item table")),
                ("asset_id", fields.UUIDField(description="FK to asset table")),
            ],
            options={"table": "link_item__asset", "app": "depot", "pk_attr": "id"},
            bases=["Model"],
        ),
    ]
