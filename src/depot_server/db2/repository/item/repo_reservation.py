from depot_server.db2.models.item.reservation import Reservation
from depot_server.db2.repository.base import AuditableRepo


class ReservationRepo(AuditableRepo):
    Db_type = Reservation
