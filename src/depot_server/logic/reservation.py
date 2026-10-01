import uuid
from uuid import UUID
from datetime import date
from datetime import timedelta

from tortoise.transactions import in_transaction

from depot_server.db2.models.item.reservation import Reservation
from depot_server.logic.contracts.reservation import CreateReservation, CollectReservation, ReturnReservation, UpdateReservationData
from depot_server.logic.results.reservation import LogicFullReservation, LogicReservationLendableLink
from depot_server.db2.repository.item.repo_reservation import ReservationRepo, ReservationRepoLinkLendable
from depot_server.logic.item import ItemService
from depot_server.logic.lendable import LendableService
from depot_server.db2.repository.base import ItemNotFound



class ReservationValidationError(ValueError):
    """Raised when reservation data cannot be fulfilled or is invalid."""


class ReservationService:
    @classmethod
    def _to_dataclass_reservation(cls, reservation: Reservation) -> LogicFullReservation:
        links = []
        for link in reservation.reservation_lendable_links:
            links.append(LogicReservationLendableLink(
                id=link.id,
                lendable_id=link.lendable_id,
                amount=link.amount,
                missing_amount=link.missing_amount,
                returned_amount=link.returned_amount,
                borrowed=link.borrowed,
                borrowed_message=link.borrowed_message,
                returned=link.returned,
                returned_message=link.returned_message
            ))
        return LogicFullReservation(
            id=reservation.id,
            user_id=reservation.user,
            name=reservation.name,
            collector=reservation.collector,
            user_notes=reservation.user_notes,
            contact=reservation.contact,
            start=reservation.start,
            end=reservation.end,
            team_id=reservation.team,
            reservation_type=reservation.reservation_type,
            importance=reservation.reservation_importance,
            links=links
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
    async def get_reserved_lendable_amount(cls, item_id, start_time: date, end_time: date, exclude_reservations: list[UUID] | None = None) -> int:
        links = await ReservationRepoLinkLendable.get_lendable_links_in_timespan(
            item_id,
            start_time,
            end_time,
            exclude_reservations=exclude_reservations
        )
        return cls._calculate_max_overlap(links)

    @classmethod
    async def create_reservation(cls, command: CreateReservation) -> LogicFullReservation:
        async with in_transaction():
            # Check if enough items are available in the specified time range
            if not await cls.are_lendables_available(command.lendables, command.start, command.end):
                raise ReservationValidationError("Not enough items available for the specified time range.")
            # Logic to create a reservation
            reservation = await ReservationRepo.create(**command.to_kwargs("name", "start", "end", "user", "team", "contact", "user_notes", "reservation_importance", "reservation_type"))
                                       
            links = []
            for lendable_id, quantity in command.lendables.items():
                if quantity <= 0:
                    raise ReservationValidationError(f"Quantity for item {lendable_id} must be greater than 0.")
                link = await ReservationRepoLinkLendable.create(reservation_id=reservation.id,
                                                                purpose_id=lendable_id,
                                                                amount=quantity
                                                                )
                links.append(LogicReservationLendableLink(
                    id=link.id,
                    lendable_id=link.purpose_id,
                    amount=link.amount,
                    missing_amount=None,
                    returned_amount=None,
                    borrowed=None,
                    borrowed_message=None,
                    returned=None,
                    returned_message=None
                ))
            return LogicFullReservation(
                id=reservation.id,
                user_id=reservation.user,
                name=reservation.name,
                collector=None,
                user_notes=reservation.user_notes,
                contact=reservation.contact,
                start=reservation.start,
                end=reservation.end,
                team_id=reservation.team,
                reservation_type=reservation.reservation_type,
                importance=reservation.reservation_importance,
                links=links
            )

    @classmethod
    async def get_reservation(cls, reservation_id: UUID) -> LogicFullReservation:
        reservation = await ReservationRepo.get_by_filter_with_links(id=reservation_id)
        if not reservation:
            raise ItemNotFound(f"Reservation with ID {reservation_id} not found.")
        return cls._to_dataclass_reservation(reservation[0])

    @classmethod
    async def get_all_reservations(cls) -> list[LogicFullReservation]:
        reservations = await ReservationRepo.get_all_with_links()
        return [cls._to_dataclass_reservation(reservation) for reservation in reservations]

    @classmethod
    async def get_reservations_by_user(cls, user_id: UUID) -> list[LogicFullReservation]:
        reservation = await ReservationRepo.get_by_filter_with_links(user=user_id)
        if not reservation:
            return []
        return [cls._to_dataclass_reservation(res) for res in reservation]

    @classmethod
    async def get_reservations_by_item(cls, item_id: UUID) -> list[LogicFullReservation]:
        reservations = await ReservationRepo.get_by_filter_with_links(
            reservation_itemlinks__item_id=item_id,
        )
        return [cls._to_dataclass_reservation(reservation) for reservation in reservations]

    @classmethod
    async def get_reservations_in_time_range(cls, start_time: date, end_time: date) -> list[LogicFullReservation]:
        reservation = await ReservationRepo.get_by_filter_with_links(start__lt=end_time + timedelta(days=1),
                                                                     end__gt=start_time - timedelta(days=1))
        if not reservation:
            return []
        return [cls._to_dataclass_reservation(res) for res in reservation]

    @classmethod
    async def update_reservation(cls, reservation_id: UUID, contract: UpdateReservationData) -> LogicFullReservation:
        async with in_transaction():
            reservation = await ReservationRepo.update(id=reservation_id,
                                                       **contract.to_kwargs("name", "start", "end", "user", "team",
                                                                            "contact", "user_notes",
                                                                            "reservation_importance",
                                                                            "reservation_type"))
            # Check if enough items are available in the specified time range
            if "links" in contract.to_kwargs("links"):
                required_lendables = {key: val.amount for key, val in contract.links.items()}
                if not await cls.are_lendables_available(required_lendables, reservation.start, reservation.end, exclude_reservations=[reservation_id]):
                    raise ReservationValidationError("Not enough items available for the specified time range.")
                
                # Update item links
                current_item_links = await ReservationRepoLinkLendable.get_by_reservation(reservation_id)
                link_ids = []
                for link in current_item_links:
                    if link.lendable_id not in contract.links.keys():
                        await ReservationRepoLinkLendable.delete_by_id(link.id)
                    else:
                        link_data = contract.links[link.lendable_id]
                        await ReservationRepoLinkLendable.update(link.id, **link_data.to_kwargs("amount", "borrowed",
                                                                        "borrowed_message", "returned", "returned_message",
                                                                        "returned_amount", "missing_amount"))

                        link_ids.append(link.lendable_id)
                # Add new item links
                for lendable_id, link_data in contract.links.items():
                    if lendable_id not in link_ids:
                        await ReservationRepoLinkLendable.create(reservation_id=reservation.id, lendable_id=lendable_id,
                                                                **link_data.to_kwargs("amount", "borrowed",
                                                                        "borrowed_message", "returned", "returned_message",
                                                                        "returned_amount", "missing_amount"))
            
        return await cls.get_reservation(reservation_id)




    @classmethod
    async def delete_reservation(cls, reservation_id: UUID):
        async with in_transaction():
            reservation = await ReservationRepo.get_by_filter_with_links(id=reservation_id)
            if not reservation:
                raise ItemNotFound(f"Reservation with ID {reservation_id} not found.")
            await ReservationRepoLinkLendable.bulk_delete(reservation.reservation_lendable_links.values_list('id', flat=True))
            await ReservationRepo.delete_by_id(id=reservation_id)

    @classmethod
    async def are_lendables_available(cls, lendables: dict[UUID, int], start_time: date, end_time: date, exclude_reservations: list[UUID] | None = None) -> bool:
        for lendable_id, quantity in lendables.items():
            total_amount = await ItemService.get_total_amount(lendable_id)
            reserved_item_amount = await cls.get_reserved_lendable_amount(lendable_id, start_time, end_time, exclude_reservations=exclude_reservations)
            if total_amount - reserved_item_amount < quantity:
                return False
        return True