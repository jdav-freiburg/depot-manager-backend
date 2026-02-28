from tortoise import fields
from tortoise.models import Model

from depot_server.config import config


class Tag(Model):
    class Meta:
        table: str = "depot_tag"

    id = fields.UUIDField(primary_key=True)
    name = fields.data.TextField(null=False)
    description = fields.data.TextField()
    color = fields.CharField(max_length=7,
                             default=config.cosmetics.tag_default_color)  # Hex color code, e.g. "#FF0000"
