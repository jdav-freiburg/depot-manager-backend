from depot_server.db2.models import ItemGroup
from depot_server.db2.repository.base import BaseRepo


class ItemGroupRepo(BaseRepo):
    Db_type = ItemGroup
