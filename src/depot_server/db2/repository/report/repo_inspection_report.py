from uuid import UUID

from depot_server.db2.models import InspectionReport
from depot_server.db2.repository.audit import AuditableRepo


class InspectionReportRepo(AuditableRepo):
    Db_type = InspectionReport

    @classmethod
    async def get_by_item_instance_id(cls, item_instance_id: UUID) -> list[InspectionReport]:
        reports = await cls.Db_type.filter(item_instance_id=item_instance_id).order_by("-created_at").all()
        return reports

