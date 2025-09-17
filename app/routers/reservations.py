from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from ..schemas import ReservationCreate, ReservationRead, ReservationCancel
from ..database import get_db

router = APIRouter(prefix="/events/{event_id}/seats/{seat_id}/reservation", tags=["reservations"])

@router.post("/", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def reserve_seat(event_id: int, seat_id: int, reservation_in: ReservationCreate, db: Session = Depends(get_db)):
    """
    Reserve a specific seat for a user
    - event_id: path parameter
    - seat_id: path parameter
    - reservation in: body with { user_id }
    - db: injected SQLAlchemy session
    """
    try:
        seat = db.query(models.Seat).filter(models.Seat.id == seat_id, models.Seat.event_id == event_id).with_for_update().first()

        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found for this event")
        
        if seat.status != "available":
            raise HTTPException(status_code=409, detail=f"Seat is not available (status: {seat.status})")
        
        db_res = models.Reservation(user_id=reservation_in.user_id, seat_id=seat.id)
        db.add(db_res)
        seat.status = "reserved"
        db.commit()
        db.refresh(db_res)
        db.refresh(seat)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not reserve seat") from e
    return db_res


@router.delete("/", status_code=status.HTTP_200_OK)
def cancel_reservation(event_id: int, seat_id: int, cancel_in: ReservationCancel, db: Session = Depends(get_db)):
    """
    Cancel reservation for a specific seat (DELETE /events/{event_id}/seats/{seat_id}/reservation)
    - Expects body: { "user_id": "<uuid>" } to verify ownership (until I add auth)
    """
    try:
        # lock the seat row to synchronize with any concurrent reservation attempts
        seat = db.query(models.Seat).filter(models.Seat.id == seat_id, models.Seat.event_id == event_id).with_for_update().first()

        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found for this event")
        
        reservation = db.query(models.Reservation).filter(models.Reservation.seat_id == seat.id).first()

        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found for this seat")
        
        # ownership check (until I put auth)
        if reservation.user_id != cancel_in.user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this reservation")
        
        # delete + free the seat in the same transation
        db.delete(reservation)
        seat.status = "available"

        db.commit()
        db.refresh(seat)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not cancel reservation") from e
    
    return {"detail": "Reservation cancelled", "seat_id": seat.id}