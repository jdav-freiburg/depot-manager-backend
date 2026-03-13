from tortoise import fields
from tortoise.models import Model


class Changelog(Model):
    class Meta:
        table: str = "depot_changelog"

    id = fields.UUIDField(primary_key=True)
    type_ = fields.CharField(max_length=100, description="The type of the object that was changed")
    type_id = fields.UUIDField(description="The identifier of the object that was changed")
    timestamp = fields.DatetimeField(auto_now_add=True)
    user_id = fields.CharField(max_length=100)
    comment = fields.data.TextField(description="'Commit' message describing why the change was made")
    old = fields.JSONField(description="The state of the object before the change")
    new = fields.JSONField(description="The state of the object after the change")
