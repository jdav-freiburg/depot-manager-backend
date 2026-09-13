from datetime import timedelta

from depot_server.db2.models.item.reservation import Reservation, ReservationItemLink, ReservationCompositeLink
from depot_server.db2.repository.audit import AuditableRepo


class ReservationRepo(AuditableRepo):
    Db_type = Reservation



class ReservationRepoLink(AuditableRepo):
    Db_type = ReservationItemLink

    @classmethod
    async def get_item_links_in_timespan(cls, item_id, start_time, end_time):
        return await cls.Db_type.filter(
            item_id=item_id,
            reservation__start__lt=end_time + timedelta(days=1),
            reservation__end__gt=start_time - timedelta(days=1)
        ).select_related("reservation")

    @classmethod
    async def get_by_reservation(cls, reservation_id):
        return await cls.Db_type.filter(
            reservation_id=reservation_id
        )


class ReservationRepoCompositeLink(AuditableRepo):
    Db_type = ReservationCompositeLink

    @classmethod
    async def get_composite_links_in_timespan(cls, composite_item_id, start_time, end_time):
        return await cls.Db_type.filter(
            composite_item_id=composite_item_id,
            reservation__start__lt=end_time + timedelta(days=1),
            reservation__end__gt=start_time - timedelta(days=1)
        ).select_related("reservation")

    @classmethod
    async def get_by_reservation(cls, reservation_id):
        return await cls.Db_type.filter(
            reservation_id=reservation_id
        )