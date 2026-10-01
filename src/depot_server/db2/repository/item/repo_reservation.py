from uuid import UUID
from datetime import timedelta

from depot_server.db2.models.item.reservation import Reservation, LinkReservationLendable, LinkReservationLinkItemInstance
from depot_server.db2.repository.audit import AuditableRepo


class ReservationRepo(AuditableRepo):
    Db_type = Reservation

    @classmethod
    async def get_all_with_links(cls) -> list[Reservation]:
        return await cls.Db_type.all().prefetch_related(
            "reservation_lendable_links",
        )

    @classmethod
    async def get_by_filter_with_links(cls, **kwargs) -> list[Reservation]:
        return await cls.Db_type.filter(**kwargs).prefetch_related(
            "reservation_lendable_links",
        )


class ReservationRepoLinkLendable(AuditableRepo):
    Db_type = LinkReservationLendable

    @classmethod
    async def get_lendable_links_in_timespan(cls, lendable_id, start_time, end_time, exclude_reservations: list[UUID] | None = None) -> list[LinkReservationLendable]:
        return await cls.Db_type.filter(
            lendable_id=lendable_id,
            reservation__start__lt=end_time + timedelta(days=1),
            reservation__end__gt=start_time - timedelta(days=1),
            reservation_id__not_in=exclude_reservations if exclude_reservations else []
        ).select_related("reservation")

    @classmethod
    async def get_by_reservation(cls, reservation_id: UUID) -> list[LinkReservationLendable]:
        return await cls.Db_type.filter(
            reservation_id=reservation_id
        )

class ReservationRepoLinkItemInstance(AuditableRepo):
    Db_type = LinkReservationLinkItemInstance