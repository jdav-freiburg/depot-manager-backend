from tortoise import fields
from tortoise.models import Model

from .report_element import ReportElement


class ReportProfile(Model):
    id = fields.UUIDField(pk=True)
    name = fields.data.TextField(unique=True)
    parent_id = fields.ForeignKeyField("report.ReportProfile", null=True)
    version = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    updated_at = fields.DatetimeField(auto_now=True)
    updated_by = fields.UUIDField()
    report_elements = fields.ManyToManyField(ReportElement, on_delete=fields.RESTRICT)
