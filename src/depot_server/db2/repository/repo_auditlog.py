from depot_server.db2.models.changelog import Changelog
from depot_server.db2.repository.base import BaseRepo


class AuditLogRepo(BaseRepo):
    Db_type = Changelog
