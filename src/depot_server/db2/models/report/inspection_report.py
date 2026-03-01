from tortoise import fields
from tortoise.models import Model

from depot_server.db2.common import Condition
from .report_profile import ReportProfile


class InspectionReport(Model):
    class Meta:
        table: str = "depot_inspection_report"

    id = fields.UUIDField(primary_key=True)

    report_profile = fields.ForeignKeyField(ReportProfile, on_delete=fields.RESTRICT, related_name="reports")
    item = fields.ForeignKeyField("depot.Item", on_delete=fields.RESTRICT, related_name="reports")

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    updated_at = fields.DatetimeField(auto_now=True)
    updated_by = fields.UUIDField()
    inspector = fields.UUIDField()
    responsible_psa_expert = fields.UUIDField()
    location = fields.CharField(blank=True, null=True, max_length=255)
    condition = fields.CharEnumField(Condition, max_length=50)
    comment = fields.data.TextField(blank=True, null=True)
