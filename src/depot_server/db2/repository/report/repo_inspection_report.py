from depot_server.db2.models import InspectionReport
from depot_server.db2.repository.base import AuditableRepo


class InspectionReportRepo(AuditableRepo):
    Db_type = InspectionReport
