from uuid import UUID
from depot_server.db2.models.item import Item
from depot_server.db2.repository.audit import AuditableRepo
from depot_server.db2.repository.base import ItemNotFound


class ItemRepo(AuditableRepo):
    Db_type = Item
