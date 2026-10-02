from datetime import date
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from depot_server.api2.models.reservation import APIReservation, APIReservationPending
from depot_server.db2.repository.base import ItemNotFound
from depot_server.logic.contracts.reservation import (
    CreateReservation,
    UpdateReservationData,
    UpdateReservationLinkData,
)
from depot_server.logic.reservation import ReservationService, ReservationValidationError


router = APIRouter(tags=["V2_Reservation"], prefix="/reservation")


def reservation_to_api(reservation) -> APIReservation:
    return APIReservation(
        id=reservation.id,
        user_id=reservation.user_id,
        name=reservation.name,
        start=reservation.start,
        end=reservation.end,
        type=reservation.reservation_type,
        importance=reservation.importance,
        team_id=reservation.team_id,
        contact=reservation.contact,
        user_notes=reservation.user_notes,
        items={link.lendable_id: link.amount for link in reservation.links},
        links=[link.__dict__ for link in reservation.links],
    )


def reservation_to_create_contract(reservation: APIReservationPending, user_id: UUID) -> CreateReservation:
    return CreateReservation(
        name=reservation.name,
        start=reservation.start,
        end=reservation.end,
        user=user_id,
        team=reservation.team_id,
        contact=reservation.contact,
        user_notes=reservation.user_notes,
        reservation_importance=reservation.importance,
        reservation_type=reservation.type,
        lendables=reservation.items,
    )


def reservation_to_update_contract(reservation: APIReservationPending) -> UpdateReservationData:
    return UpdateReservationData(
        name=reservation.name,
        start=reservation.start,
        end=reservation.end,
        team=reservation.team_id,
        contact=reservation.contact,
        user_notes=reservation.user_notes,
        reservation_importance=reservation.importance,
        reservation_type=reservation.type,
        links={
            lendable_id: UpdateReservationLinkData(amount=amount)
            for lendable_id, amount in reservation.items.items()
        },
    )


@router.get("/")
async def get_all_reservations() -> list[APIReservation]:
    reservations = await ReservationService.get_all_reservations()
    return [reservation_to_api(reservation) for reservation in reservations]


@router.get("/user/{user_id}")
async def get_reservations_by_user(user_id: UUID) -> list[APIReservation]:
    reservations = await ReservationService.get_reservations_by_user(user_id)
    return [reservation_to_api(reservation) for reservation in reservations]


@router.get("/lendable/{lendable_id}")
async def get_reservations_by_lendable(lendable_id: UUID) -> list[APIReservation]:
    reservations = await ReservationService.get_reservations_by_lendable(lendable_id)
    return [reservation_to_api(reservation) for reservation in reservations]


@router.get("/time-range/{start_date}/{end_date}")
async def get_reservations_in_time_range(start_date: date, end_date: date) -> list[APIReservation]:
    reservations = await ReservationService.get_reservations_in_time_range(start_date, end_date)
    return [reservation_to_api(reservation) for reservation in reservations]


@router.get("/{reservation_id}")
async def get_reservation(reservation_id: UUID) -> APIReservation:
    try:
        reservation = await ReservationService.get_reservation(reservation_id)
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    return reservation_to_api(reservation)


@router.post("/")
async def create_reservation(reservation_data: APIReservationPending) -> APIReservation:
    try:
        reservation = await ReservationService.create_reservation(
            reservation_to_create_contract(reservation_data, uuid4())
        )
    except ReservationValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex)) from ex
    return reservation_to_api(reservation)


@router.put("/{reservation_id}")
async def update_reservation(reservation_id: UUID, reservation_data: APIReservationPending) -> APIReservation:
    try:
        reservation = await ReservationService.update_reservation(
            reservation_id, reservation_to_update_contract(reservation_data)
        )
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ReservationValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex)) from ex
    return reservation_to_api(reservation)


@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: UUID) -> None:
    try:
        await ReservationService.delete_reservation(reservation_id)
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex