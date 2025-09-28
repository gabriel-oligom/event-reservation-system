from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from .. import models
from ..database import get_db
from ..utils import expire_holds

router = APIRouter(prefix="/events/{event_id}/seats/{seat_id}/hold", tags=["holds"])

MAX_HOLD_SECONDS = 60
MAX_HOLDS_PER_USER_PER_EVENT = 3


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_hold(event_id: int, seat_id: int, body: dict, db: Session = Depends(get_db)):
    """
    body: { "user_id": "<uuid>", "seconds": 60}
    """
    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    
    seconds = int(body.get("seconds", MAX_HOLD_SECONDS))
    if seconds <= 0 or seconds > MAX_HOLD_SECONDS:
        raise HTTPException(status_code=400, detail=f"seconds must be between 1 and {MAX_HOLD_SECONDS}")
    
    # Pass the current event ID to expire_holds to clean up expired holds for this event only
    expire_holds(db, event_id=event_id)

    try:
        # Lock the seat row to prevent race conditions during update
        seat = db.query(models.Seat).filter(models.Seat.id == seat_id, models.Seat.event_id == event_id).with_for_update().first()
        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found for this event")
        
        if seat == "reserved":
            raise HTTPException(status_code=409, detail="Seat already reserved")
        
        # check if seat already on hold (someone else)
        if seat.status == "on_hold":
            # check if hold belongs to same user
            existing_hold = db.query(models.Hold.seat_id == models.Seat.id).first()
            if existing_hold and existing_hold.user_id == user_id:
                raise HTTPException(status_code=409, detail="You already hold this seat")
            raise HTTPException(status_code=409, detail="Seat already on hold")
        
        now = datetime.now(timezone.utc)

        # Count active holds for this user in the same event
        user_holds_count = (db.query(models.Hold)
                            .join(models.Seat, models.Hold.seat_id == models.Seat.id)
                            .filter(models.Seat.event_id == event_id, models.Hold.user_id == user_id, models.Hold.expires_at > now)
                            .count())
        if user_holds_count >= MAX_HOLDS_PER_USER_PER_EVENT:
            raise HTTPException(status_code=409, detail="User holds limit reached for this event")
        
        # create hold
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        hold = models.Hold(user_id=user_id, seat_id=seat.id, held_at=datetime.now(timezone.utc), expires_at=expires_at)
        db.add(hold)
        seat.status = "on_hold"
        db.commit
        db.refresh(hold)
        db.refresh(seat)

    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=500, detaill="could not create hold") from e
    
    return {
        "seat": seat.id, 
        "user_id": hold.user_id, 
        "expires_at": hold.expires_at.isoformat()
        }


@router.put("/", status_code=status.HTTP_200_OK)
def refresh_hold(event_id: int, seat_id: int, body: dict, db: Session = Depends(get_db)):
    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    seconds = int(body.get("seconds", MAX_HOLD_SECONDS))
    if seconds <= 0 or seconds > MAX_HOLD_SECONDS:
        raise HTTPException(status_code=400, detail=f"seconds must be between 1 and {MAX_HOLD_SECONDS}")
    expire_holds(db, event_id=event_id)

    try:
        seat = db.query(models.Seat).filter(models.Seat.id == seat_id, models.Seat.event_id == event_id).with_for_update().first()
        if not seat:
            HTTPException(status_code=404, detail="Seat not found")

        # Find the current hold for this seat
        hold = db.query(models.Hold).filter(models.Hold.seat_id == seat.id).first()
        if not hold:
            raise HTTPException(status_code=403, detail="No active hold for this user on this seat")
        
        # Update expiration time for the hold
        hold.expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        db.commit()
        db.refresh(hold)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could nt=ot refresh holf") from e
    
    return {
        "seat_id": seat.id,
        "expires_at": hold.expires_at.isoformat()
        }


@router.delete("/", status_code=status.HTTP_200_OK)
def cancel_hold(event_id: int, seat_id: int, body: dict, db: Session = Depends(get_db)):
    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    try:
        seat = db.query(models.Seat).filter(models.Seat.id == seat_id, models.Seat.event_id == event_id).with_for_update().first()
        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found")
        
        hold = db.query(models.Hold).filter(models.Hold.seat_id == seat.id).first()
        if not hold:
            raise HTTPException(status_code=404, detail="Hold not found")
        if hold.user_id != user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this hold")
        
        db.delete(hold)
        seat.status = "available"
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not cancel hold") from e
    
    return {
        "detail": "Hold cancelled", 
        "seat_id": seat.id
        }