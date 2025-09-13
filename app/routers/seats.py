from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..schemas import SeatRead
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