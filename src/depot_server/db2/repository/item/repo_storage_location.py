from depot_server.db2.models import StorageLocation
from depot_server.db2.repository.base import BaseRepo


class StorageLocationRepo(BaseRepo):
    Db_type = StorageLocation
