from tortoise import fields
from tortoise.models import Model


class AllowedMimeType(Model):

    class Meta:
        table: str = "depot_allowed_mimetype"

    mime = fields.data.CharField(null=False, pk=True, max_length=50)
    description = fields.data.TextField()
