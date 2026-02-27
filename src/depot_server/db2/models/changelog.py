from tortoise import fields
from tortoise.models import Model


class Changelog(Model):
    class Meta:
        table: str = "depot_changelog"

    id = fields.UUIDField(primary_key=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    user_id = fields.CharField(max_length=100)
    comment = fields.data.TextField()
    changes = fields.JSONField()
    report = fields.JSONField()
