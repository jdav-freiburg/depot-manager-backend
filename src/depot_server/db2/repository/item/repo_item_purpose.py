
from depot_server.db2.repository.audit import AuditableRepo
from depot_server.db2.models.item.item_purpose import ItemPurpose

class ItemPurposeRepo(AuditableRepo):
    Db_type = ItemPurpose