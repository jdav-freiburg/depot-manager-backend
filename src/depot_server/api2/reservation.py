from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.base import ItemNotFound
from depot_server.api2.models.reservation import APIReservationPending, APIReservation
from depot_server.logic.reservation import ReservationService
from depot_server.logic.reservation import ReservationService, ReservationValidationError

router = APIRouter(tags=["V2_Reservation"])

@router.get("/reservations")
async def get_all_reservations() -> list[APIReservation]:
    """
    Get all reservations.
    """
    reservations = await ReservationService.get_all_reservations()
    return [APIReservation.model_validate(r) for r in reservations]


@router.get("/reservations/{reservation_id}")
async def get_reservation(reservation_id: UUID) -> APIReservation:
    """
    Get a reservation by its ID.
    """
    try:
        reservation = await ReservationService.get_reservation(reservation_id)
        return APIReservation.model_validate(reservation)
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/reservations/user/{user_id}")
async def get_reservations_by_user(user_id: UUID) -> list[APIReservation]:
    """
    Get reservations for a specific user.
    """
    reservations = await ReservationService.get_reservations_by_user(user_id)
    return [APIReservation.model_validate(r) for r in reservations]

@router.get("/reservations/item/{item_id}")
async def get_reservations_by_item(item_id: UUID) -> list[APIReservation]:
    """
    Get reservations for a specific item in chronological order.
    
    Parameters:
    - item_id: The ID of an item, not an item instance.
    """
    reservations = await ReservationService.get_reservations_by_item(item_id)
    return [APIReservation.model_validate(r) for r in reservations]



@router.get("/reservations/time-range/{start_date}/{end_date}")
async def get_reservations_in_time_range(start_date: date, end_date: date) -> list[APIReservation]:
    """
    Get reservations within a specific time range.
    
    Parameters:
    - start_date: The start of the date range (ISO 8601 format).
    - end_date: The end of the date range (ISO 8601 format).
    """
    reservations = await ReservationService.get_reservations_in_time_range(start_date, end_date)
    return [APIReservation.model_validate(r) for r in reservations]


@router.post("/reservations")
async def create_reservation(reservation_data: APIReservationPending) -> APIReservation:
    """
    Create a new reservation.
    """
    try:
        reservation = await ReservationService.create_reservation(reservation_data)
        return APIReservation.model_validate(reservation)
    except ReservationValidationError as ex:
        raise HTTPException(status_code=422, detail=str(ex)) from ex


@router.put("/reservations/{reservation_id}")
async def update_reservation(reservation_id: UUID, reservation_data: APIReservationPending) -> APIReservation:
    """
    Update an existing reservation by its ID.
    """
    try:
        updated_reservation = await ReservationService.update_reservation(reservation_id, reservation_data)
        return APIReservation.model_validate(updated_reservation)
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