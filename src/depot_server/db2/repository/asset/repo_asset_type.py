from depot_server.db2.models import AssetType
from depot_server.db2.repository.base import BaseRepo


class AssetTypeRepo(BaseRepo):
    Db_type = AssetType
