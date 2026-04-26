from depot_server.db2.models.asset.mime_type import AllowedMimeType
from depot_server.db2.repository.base import BaseRepo


class MimeTypeRepo(BaseRepo):
    Db_type = AllowedMimeType
