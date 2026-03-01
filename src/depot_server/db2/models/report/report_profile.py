from tortoise import fields
from tortoise.models import Model

from .report_element import ReportElement


class ReportProfile(Model):
    class Meta:
        table: str = "depot_report_profile"

    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=100, unique=True)
    parent_id = fields.ForeignKeyField("depot.ReportProfile", null=True, related_name="child")
    version = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    updated_at = fields.DatetimeField(auto_now=True)
    updated_by = fields.UUIDField()
    report_elements = fields.ManyToManyField(ReportElement, on_delete=fields.RESTRICT)

    @property
    def is_latest(self) -> bool:
        return self.parent_id is None
