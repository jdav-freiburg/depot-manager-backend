from depot_server.db2.models import Item
from depot_server.db2.repository.audit import AuditableRepo


class ItemRepo(AuditableRepo):
    Db_type = Item
