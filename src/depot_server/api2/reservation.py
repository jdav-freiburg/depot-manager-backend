from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.base import ItemNotFound
from depot_server.api2.models.reservation import ReservationPending, Reservation
from depot_server.logic.reservation import ReservationService
from depot_server.logic.reservation import ReservationService, ReservationValidationError

router = APIRouter()

@router.get("/reservations")
async def get_all_reservations() -> list[Reservation]:
    """
    Get all reservations.
    """
    reservations = await ReservationService.get_all_reservations()
    return reservations


@router.get("/reservations/{reservation_id}")
async def get_reservation(reservation_id: UUID) -> Reservation:
    """
    Get a reservation by its ID.
    """
    try:
        reservation = await ReservationService.get_reservation(reservation_id)
        return reservation
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/reservations/user/{user_id}")
async def get_reservations_by_user(user_id: UUID) -> list[Reservation]:
    """
    Get reservations for a specific user.
    """
    reservations = await ReservationService.get_reservations_by_user(user_id)
    return reservations

@router.get("/reservations/item/{item_id}")
async def get_reservations_by_item(item_id: UUID) -> list[Reservation]:
    """
    Get reservations for a specific item in chronological order.
    
    Parameters:
    - item_id: The ID of an item, not an item instance.
    """
    reservations = await ReservationService.get_reservations_by_item(item_id)
    return reservations


@router.get("/reservations/time-range/{start_time}/{end_time}")
async def get_reservations_in_time_range(start_time: datetime, end_time: datetime) -> list[Reservation]:
    """
    Get reservations within a specific time range.
    
    Parameters:
    - start_time: The start of the time range (ISO 8601 format).
    - end_time: The end of the time range (ISO 8601 format).
    """
    reservations = await ReservationService.get_reservations_in_time_range(start_time, end_time)
    return reservations


@router.post("/reservations")
async def create_reservation(reservation_data: ReservationPending) -> Reservation:
    """
    Create a new reservation.
    """
    try:
        reservation = await ReservationService.create_reservation(reservation_data)
        return reservation
    except ReservationValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex)) from ex


@router.put("/reservations/{reservation_id}")
async def update_reservation(reservation_id: UUID, reservation_data: ReservationPending) -> Reservation:
    """
    Update an existing reservation by its ID.
    """
    try:
        updated_reservation = await ReservationService.update_reservation(reservation_id, reservation_data)
        return updated_reservation
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ReservationValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex)) from ex


@router.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: UUID) -> dict:
    """
    Delete a reservation by its ID.
    """
    try:
        await ReservationService.delete_reservation(reservation_id)
        return {"message": "Reservation deleted successfully."}
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex