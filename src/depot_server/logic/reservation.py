import uuid
from uuid import UUID
from datetime import date
from datetime import timedelta

from tortoise.transactions import in_transaction

from depot_server.api2.models.reservation import Reservation, ReservationPending
from depot_server.db2.repository.item.repo_reservation import ReservationRepo, ReservationRepoLink, ReservationRepoCompositeLink
from depot_server.logic.item import ItemService
from depot_server.logic.lendable import LendableService
from depot_server.db2.repository.base import ItemNotFound


class ReservationValidationError(ValueError):
    """Raised when reservation data cannot be fulfilled or is invalid."""


class ReservationService:
    @staticmethod
    def _to_api_reservation(reservation, elements=None, composites=None) -> Reservation:
        elements = (
            reservation.reservation_itemlinks
            if elements is None
            else elements
        )
        composites = (
            reservation.reservation_composite_itemlinks
            if composites is None
            else composites
        )
        return Reservation(
            id=reservation.id,
            user_id=reservation.user,
            name=reservation.name,
            start=reservation.start,
            end=reservation.end,
            type=reservation.reservation_type,
            importance=reservation.reservation_importance,
            team_id=reservation.team,
            contact=reservation.contact,
            user_notes=reservation.user_notes,
            items={link.item_id: link.amount for link in elements},
            composite_items={
                link.composite_item_id: link.amount
                for link in composites
            },
        )

    @staticmethod
    def _calculate_max_overlap(links) -> int:
        if not links:
            return 0
        pickups = {}
        bringbacks = {}
        for link in links:
            pickups[link.reservation.start] = pickups.get(link.reservation.start, 0) + link.amount
            bringbacks[link.reservation.end] = bringbacks.get(link.reservation.end, 0) + link.amount

        pickup_keys = sorted(pickups.keys())
        bringback_keys = sorted(bringbacks.keys())

        amount = 0
        max_amount = 0
        bringback_index = 0
        bringback_max_index = len(bringback_keys) - 1
        next_bringback_time = bringback_keys[0]
        for i, pickup_time in enumerate(pickup_keys):
            while bringback_index <= bringback_max_index and next_bringback_time < pickup_time:
                amount -= bringbacks[next_bringback_time]
                bringback_index += 1
                if bringback_index <= bringback_max_index:
                    next_bringback_time = bringback_keys[bringback_index]
            amount += pickups[pickup_time]
            max_amount = max(max_amount, amount)
        return max_amount


    @classmethod
    async def get_reserved_item_amount(cls, item_id, start_time: date, end_time: date, exclude_reservations: list[UUID] | None = None) -> int:
        links = await ReservationRepoLink.get_item_links_in_timespan(
            item_id,
            start_time,
            end_time,
            exclude_reservations=exclude_reservations
        )
        return cls._calculate_max_overlap(links)

    @classmethod
    async def get_reserved_composite_amount(cls, composite_item_id, start_time: date, end_time: date, exclude_reservations: list[UUID] | None = None) -> int:
        links = await ReservationRepoCompositeLink.get_composite_links_in_timespan(
            composite_item_id,
            start_time,
            end_time,
            exclude_reservations=exclude_reservations
        )
        return cls._calculate_max_overlap(links)

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
                                                borrowed=None)
            for item_composite_id, quantity in reservation_data.composite_items.items():
                await ReservationRepoCompositeLink.create(reservation_id=reservation.id,
                                                        composite_item_id=item_composite_id,
                                                        amount=quantity,
                                                        borrowed=None)
            return Reservation(id=reservation.id, user_id=reservation.user, **reservation_data.model_dump())

    @classmethod
    async def get_reservation(cls, reservation_id) -> Reservation:
        reservation = await ReservationRepo.get_by_filter_with_links(id=reservation_id)
        if not reservation:
            raise ItemNotFound(f"Reservation with ID {reservation_id} not found.")
        return cls._to_api_reservation(reservation[0])

    @classmethod
    async def get_all_reservations(cls) -> list[Reservation]:
        reservations = await ReservationRepo.get_all_with_links()
        return [cls._to_api_reservation(reservation) for reservation in reservations]

    @classmethod
    async def get_reservations_by_user(cls, user_id: UUID) -> list[Reservation]:
        reservation = await ReservationRepo.get_by_filter_with_links(user=user_id)
        if not reservation:
            return []
        return [cls._to_api_reservation(res) for res in reservation]

    @classmethod
    async def get_reservations_by_item(cls, item_id: UUID) -> list[Reservation]:
        reservations = await ReservationRepo.get_by_filter_with_links(
            reservation_itemlinks__item_id=item_id,
        )
        return [cls._to_api_reservation(reservation) for reservation in reservations]

    @classmethod
    async def get_reservations_in_time_range(cls, start_time: date, end_time: date) -> list[Reservation]:
        reservation = await ReservationRepo.get_by_filter_with_links(start__lt=end_time + timedelta(days=1),
                                                                     end__gt=start_time - timedelta(days=1))
        if not reservation:
            return []
        return [cls._to_api_reservation(res) for res in reservation]

    @classmethod
    async def update_reservation(cls, reservation_id: UUID, update_data: ReservationPending) -> Reservation:
        async with in_transaction():
            # Check if enough items are available in the specified time range
            if not await cls.are_items_available(update_data.items, update_data.composite_items, update_data.start, update_data.end, exclude_reservations=[reservation_id]):
                raise ReservationValidationError("Not enough items available for the specified time range.")
            
            reservation = await ReservationRepo.update(id=reservation_id, name=update_data.name,
                                                       start=update_data.start,
                                                       end=update_data.end,
                                                       user=uuid.uuid4(),  # TODO get actual user
                                                       team=update_data.team_id,
                                                       contact=update_data.contact,
                                                       user_notes=update_data.user_notes,
                                                       reservation_importance=update_data.importance,
                                                       reservation_type=update_data.type)
            if not reservation:
                raise ItemNotFound(f"Reservation with ID {reservation_id} not found.")
            # Update item links
            current_item_links = await ReservationRepoLink.get_by_reservation(reservation_id)
            item_ids = []
            for link in current_item_links:
                if link.item_id not in update_data.items:
                    await ReservationRepoLink.delete_by_id(link.id)
                else:
                    await ReservationRepoLink.update(link.id, amount=update_data.items[link.item_id])
                    item_ids.append(link.item_id)
            # Add new item links
            for item_id, amount in update_data.items.items():
                if item_id not in item_ids:
                    await ReservationRepoLink.create(reservation_id=reservation.id, item_id=item_id, amount=amount)
            # Update composite item links
            current_composite_links = await ReservationRepoCompositeLink.get_by_reservation(reservation_id)
            composite_ids = []
            for link in current_composite_links:
                if link.composite_item_id not in update_data.composite_items:
                    await ReservationRepoCompositeLink.delete_by_id(link.id)
                else:
                    await ReservationRepoCompositeLink.update(link.id, amount=update_data.composite_items[link.composite_item_id])
                    composite_ids.append(link.composite_item_id)
            # Add new composite item links
            for composite_item_id, amount in update_data.composite_items.items():
                if composite_item_id not in composite_ids:
                    await ReservationRepoCompositeLink.create(reservation_id=reservation.id, composite_item_id=composite_item_id, amount=amount)
        return await cls.get_reservation(reservation_id)




    @classmethod
    async def delete_reservation(cls, reservation_id):
        async with in_transaction():
            reservation = await ReservationRepo.get_by_filter_with_links(id=reservation_id)
            if not reservation:
                raise ItemNotFound(f"Reservation with ID {reservation_id} not found.")
            await ReservationRepoLink.bulk_delete(reservation_id.reservation_links.values_list('id', flat=True))
            await ReservationRepoCompositeLink.bulk_delete(reservation_id.reservation_composite_links.values_list('id', flat=True))
            await ReservationRepo.delete_by_id(id=reservation_id)

    @classmethod
    async def are_items_available(cls, items: dict[UUID, int], item_composites: dict[UUID, int], start_time: date, end_time: date, exclude_reservations: list[UUID] | None = None) -> bool:
        for item_id, quantity in items.items():
            total_amount = await ItemService.get_total_amount(item_id)
            reserved_item_amount = await cls.get_reserved_item_amount(item_id, start_time, end_time, exclude_reservations=exclude_reservations)
            if total_amount - reserved_item_amount < quantity:
                return False
            
        for composite_item_id, quantity in item_composites.items():
            available_amount = await LendableService.get_total_amount(composite_item_id)
            reserved_composite_amount = await cls.get_reserved_composite_amount(composite_item_id, start_time, end_time, exclude_reservations=exclude_reservations)
            if available_amount - reserved_composite_amount < quantity:
                return False
        return True