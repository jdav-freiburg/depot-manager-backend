from datetime import datetime

from fastapi import APIRouter, HTTPException

from depot_server.db2.repository.base import ItemNotFound
from depot_server.logic.reservation import ReservationService

router = APIRouter()

@router.get("/reservations")
async def get_all_reservations():
    """
    Get all reservations.
    """
    reservations = ReservationService.get_all_reservations()
    return reservations


@router.get("/reservations/{reservation_id}")
async def get_reservation(reservation_id: str):
    """
    Get a reservation by its ID.
    """
    try:
        reservation = ReservationService.get_reservation(reservation_id)
        return reservation
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/reservations/user/{user_id}")
async def get_reservations_by_user(user_id: str):
    """
    Get reservations for a specific user.
    """
    reservations = ReservationService.get_reservations_by_user(user_id)
    return reservations

@router.get("/reservations/item/{item_id}")
async def get_reservations_by_item(item_id: str):
    """
    Get reservations for a specific item.
    
    Parameters:
    - item_id: The ID of an itemgroup that contains only one item.
    """
    reservations = ReservationService.get_reservations_by_item(item_id)
    return reservations


@router.get("/reservations/time-range/{start_time}/{end_time}")
async def get_reservations_in_time_range(start_time: datetime, end_time: datetime):
    """
    Get reservations within a specific time range.
    
    Parameters:
    - start_time: The start of the time range (ISO 8601 format).
    - end_time: The end of the time range (ISO 8601 format).
    """
    reservations = ReservationService.get_reservations_in_time_range(start_time, end_time)
    return reservations


@router.post("/reservations")
async def create_reservation(reservation_data: dict):
    """
    Create a new reservation.
    """
    try:
        reservation = ReservationService.create_reservation(reservation_data)
        return reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/reservations/{reservation_id}")
async def update_reservation(reservation_id: str, reservation_data: dict):
    """
    Update an existing reservation by its ID.
    """
    try:
        updated_reservation = ReservationService.update_reservation(reservation_id, reservation_data)
        return updated_reservation
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: str):
    """
    Delete a reservation by its ID.
    """
    try:
        ReservationService.delete_reservation(reservation_id)
        return {"message": "Reservation deleted successfully."}
    except ItemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))