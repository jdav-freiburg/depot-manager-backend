from depot_server.db2.models import ExternalService
from depot_server.db2.repository.base import BaseRepo


class ExternalServiceRepo(BaseRepo):
    Db_type = ExternalService
