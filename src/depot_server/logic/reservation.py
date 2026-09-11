import uuid
from uuid import UUID
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from tortoise.transactions import in_transaction

from depot_server.api2.models.reservation import Reservation, ReservationPending
from depot_server.db2.repository.item.repo_reservation import ReservationRepo, ReservationRepoLink, ReservationRepoCompositeLink
from depot_server.logic.item import ItemService
from depot_server.logic.item_composite import ItemCompositeService
from depot_server.db2.repository.base import ItemNotFound


class ReservationValidationError(ValueError):
    """Raised when reservation data cannot be fulfilled or is invalid."""


class ReservationService:
    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _calculate_max_reserved_amount(links, start_time: datetime, end_time: datetime) -> int:
        start_time = ReservationService._normalize_datetime(start_time)
        end_time = ReservationService._normalize_datetime(end_time)
        if start_time > end_time:
            return 0

        changes = {}
        for link in links:
            reservation_start = max(ReservationService._normalize_datetime(link.reservation.start), start_time)
            reservation_end = min(ReservationService._normalize_datetime(link.reservation.end) + timedelta(days=1), end_time)
            changes[reservation_start] = changes.get(reservation_start, 0) + link.amount
            changes[reservation_end] = changes.get(reservation_end, 0) - link.amount

        reserved_amount = 0
        maximum_reserved_amount = 0
        for timestamp in sorted(changes):
            reserved_amount += changes[timestamp]
            maximum_reserved_amount = max(maximum_reserved_amount, reserved_amount)

        return maximum_reserved_amount

    @classmethod
    async def get_reserved_item_amount(cls, item_id, start_time: datetime, end_time: datetime) -> int:
        links = await ReservationRepoLink.get_by_item(
            item_id,
            start_time,
            end_time,
        )
        return cls._calculate_max_reserved_amount(links, start_time, end_time)

    @classmethod
    async def get_reserved_composite_amount(cls, composite_item_id, start_time: datetime, end_time: datetime) -> int:
        links = await ReservationRepoCompositeLink.get_links_for_composite_item(
            composite_item_id,
            start_time,
            end_time,
        )
        return cls._calculate_max_reserved_amount(links, start_time, end_time)

    @classmethod
    async def create_reservation(cls, reservation_data: ReservationPending) -> Reservation:
        async with in_transaction():
            # Check if enough items are available in the specified time range
            if not await cls.are_items_available(reservation_data.items, reservation_data.composite_items, reservation_data.start, reservation_data.end):
                raise ReservationValidationError("Not enough items available for the specified time range.")
            # Logic to create a reservation
            reservation = await ReservationRepo.create(name=reservation_data.name,
                                        start=reservation_data.start,
                                        end=reservation_data.end,
                                        user= uuid.uuid4(),  # TODO get actual user
                                        team=reservation_data.team_id,
                                        contact=reservation_data.contact,
                                        #active=reservation_data.active,
                                        user_notes=reservation_data.user_notes,
                                        reservation_importance=reservation_data.importance,
                                        reservation_type=reservation_data.type,
                                        borrowed=None)
            for item_id, quantity in reservation_data.items.items():
                if quantity <= 0:
                    raise ReservationValidationError(f"Quantity for item {item_id} must be greater than 0.")
                await ReservationRepoLink.create(reservation_id=reservation.id,
                                                item_id=item_id,
                                                amount=quantity,
                                                borrowed=False)
            for item_composite_id, quantity in reservation_data.composite_items.items():
                await ReservationRepoCompositeLink.create(reservation_id=reservation.id,
                                                        composite_item_id=item_composite_id,
                                                        amount=quantity,
                                                        borrowed=False)
            return Reservation(id=reservation.id, user_id=reservation.user, **reservation_data.model_dump())

    @classmethod
    async def get_reservation(cls, reservation_id) -> Reservation:
        reservation = await ReservationRepo.get_by_id(reservation_id)
        if not reservation:
            raise ItemNotFound(f"Reservation with ID {reservation_id} not found.")
        elements = await ReservationRepoLink.get_by_reservation(reservation_id)
        composites = await ReservationRepoCompositeLink.get_by_reservation(reservation_id)
        
        return Reservation(id=reservation.id, user_id=reservation.user,
                           items={e.item_id: e.amount for e in elements},
                           composite_items={c.composite_item_id: c.amount for c in composites},
                           **reservation.model_dump())

    @classmethod
    async def get_all_reservations(cls) -> list[Reservation]:
        # Logic to retrieve all reservations
        raise NotImplementedError("This method is not yet implemented.")

    @classmethod
    async def get_reservations_by_user(cls, user_id):
        # Logic to retrieve reservations by user ID
        raise NotImplementedError("This method is not yet implemented.")

    @classmethod
    async def get_reservations_by_item(cls, item_id):
        # Logic to retrieve reservations by item ID
        raise NotImplementedError("This method is not yet implemented.")

    @classmethod
    async def get_reservations_in_time_range(cls, start_time, end_time):
        # Logic to retrieve reservations in a specific time range
        raise NotImplementedError("This method is not yet implemented.")

    @classmethod
    async def update_reservation(cls, reservation_id, update_data):
        # Logic to update a reservation
        raise NotImplementedError("This method is not yet implemented.")

    @classmethod
    async def delete_reservation(cls, reservation_id):
        # Logic to delete a reservation
        raise NotImplementedError("This method is not yet implemented.")

    @classmethod
    async def are_items_available(cls, items: dict[UUID, int], item_composites: dict[UUID, int], start_time: datetime, end_time: datetime) -> bool:
        for item_id, quantity in items.items():
            total_amount = await ItemService.get_total_amount(item_id)
            reserved_item_amount = await cls.get_reserved_item_amount(item_id, start_time, end_time)
            if total_amount - reserved_item_amount < quantity:
                return False
            
        for composite_item_id, quantity in item_composites.items():
            available_amount = await ItemCompositeService.get_total_amount(composite_item_id)
            reserved_composite_amount = await cls.get_reserved_composite_amount(composite_item_id, start_time, end_time)
            if available_amount - reserved_composite_amount < quantity:
                return False
        return True