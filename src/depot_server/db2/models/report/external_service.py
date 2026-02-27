from tortoise import fields
from tortoise.models import Model


class ExternalService(Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    updated_at = fields.DatetimeField()
    updated_by = fields.UUIDField()
    reason = fields.data.TextField()
    intern_responsible = fields.data.TextField()
    service_contractor = fields.data.TextField()
    notes = fields.data.TextField()
