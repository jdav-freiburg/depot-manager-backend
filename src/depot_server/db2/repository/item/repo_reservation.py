from depot_server.db2.models.item.reservation import Reservation, ReservationItemLink, ReservationCompositeLink
from depot_server.db2.repository.audit import AuditableRepo


class ReservationRepo(AuditableRepo):
    Db_type = Reservation

    @classmethod
    async def get_links_for_item(cls, item_id, start_time, end_time):
        return await ReservationItemLink.filter(
            item_id=item_id,
            reservation__start__lt=end_time,
            reservation__end__gt=start_time,
        ).select_related("reservation")



class ReservationRepoLink(AuditableRepo):
    Db_type = ReservationItemLink


class ReservationRepoCompositeLink(AuditableRepo):
    Db_type = ReservationCompositeLink

    @classmethod
    async def get_links_for_composite_item(cls, composite_item_id, start_time, end_time):
        return await cls.Db_type.filter(
            composite_item_id=composite_item_id,
            reservation__start__lt=end_time,
            reservation__end__gt=start_time,
        ).select_related("reservation")
