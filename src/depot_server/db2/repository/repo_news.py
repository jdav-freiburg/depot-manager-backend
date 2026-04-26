from depot_server.db2.models.news import NewsEntry
from depot_server.db2.repository.base import BaseRepo


class NewsRepo(BaseRepo):
    Db_type = NewsEntry
