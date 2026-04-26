from depot_server.api.models import Reservation
from depot_server.db2.repository.base import AuditableRepo


class ReservationRepo(AuditableRepo):
    Db_type = Reservation
