from depot_server.db2.models.item.reservation import Reservation, ReservationGroupLink, ReservationCompositeLink
from depot_server.db2.repository.audit import AuditableRepo


class ReservationRepo(AuditableRepo):
    Db_type = Reservation

    @classmethod
    async def get_links_for_item_group(cls, item_group_id, start_time, end_time):
        return await ReservationGroupLink.filter(
            item_group_id=item_group_id,
            reservation__start__lt=end_time,
            reservation__end__gt=start_time,
        ).select_related("reservation")



class ReservationRepoLink(AuditableRepo):
    Db_type = ReservationGroupLink


class ReservationRepoCompositeLink(AuditableRepo):
    Db_type = ReservationCompositeLink
