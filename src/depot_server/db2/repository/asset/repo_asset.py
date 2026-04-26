from depot_server.db2.models import Asset
from depot_server.db2.repository.base import BaseRepo


class AssetRepo(BaseRepo):
    Db_type = Asset
