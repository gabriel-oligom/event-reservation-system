from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from ..schemas import ReservationCreate, ReservationRead
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