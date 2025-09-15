from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..schemas import SeatRead, ReservationCreate, ReservationRead
from ..database import get_db

router = APIRouter(prefix="/events/{event_id}/seats", tags=["seats"])

@router.get("/", response_model=List[SeatRead])
def read_event_seats(event_id, db: Session = Depends(get_db)):
    """
    Return all seats for a given event
    - event_id: path parameter (int)
    - db: SQLAlchemy Session injected by Depends(get_db)
    """
    event = db.get(models.Event, event_id) # To ensure that event exists (gives 404 if not)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    seats = db.query(models.Seat).filter(models.Seat.event_id == event_id).order_by(models.Seat.number).all()
    return seats

@router.get("/{seat_id}", response_model=SeatRead)
def read_event_seat(event_id: int, seat_id: int, db: Session = Depends(get_db)):
    """
    Return a single seat for a given event
    - URL: GET /events/{event_id}/seats/{seat_id}
    """

    # A query for the seat that has this ID and belongs to this event
    seat = db.query(models.Seat).filter(models.Seat.id == seat_id, models.Seat.event_id == event_id).first()

    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found for this event")
    return seat


@router.post("/{seat_id}/reserve", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
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