from depot_server.db2.models import ReportProfile
from depot_server.db2.repository.audit import AuditableRepo


class ReportProfileRepo(AuditableRepo):
    Db_type = ReportProfile
