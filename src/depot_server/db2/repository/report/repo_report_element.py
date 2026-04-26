from depot_server.db2.models import ReportElement
from depot_server.db2.repository.base import AuditableRepo


class ReportElementRepo(AuditableRepo):
    Db_type = ReportElement
