from tortoise import fields
from tortoise.models import Model


class NewsEntry(Model):
    class Meta:
        table: str = "depot_news_entry"

    id = fields.UUIDField(primary_key=True)

    title = fields.CharField(max_length=255, null=False, blank=False)
    timestamp = fields.DatetimeField(auto_now_add=True)
    author = fields.UUIDField(null=False)
    text = fields.data.TextField(null=True)
    expires = fields.DatetimeField(auto_now_add=True)
    is_visible = fields.BooleanField(default=True)
    is_pinned = fields.BooleanField(default=False)
