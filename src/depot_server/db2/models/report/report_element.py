from tortoise import fields
from tortoise.models import Model

from depot_server.db2.common import UserIdField


class ReportElement(Model):
    class Meta:
        table: str = "depot_report_element"

    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=100, unique=True)
    parent_id = fields.ForeignKeyField("depot.ReportElement", null=True, related_name="child")
    version = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    created_bv = fields.UUIDField()
    updated_at = fields.DatetimeField()
    updated_by: UserIdField = fields.UUIDField()
