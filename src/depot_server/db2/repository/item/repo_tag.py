from depot_server.db2.models import Tag
from depot_server.db2.repository.base import AuditableRepo


class TagRepo(AuditableRepo):
    Db_type = Tag
