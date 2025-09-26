from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from .. import models
from ..database import get_db
from ..utils import expire_holds

router = APIRouter(prefix="/events/{event_id}/seats/{seat_id}/hold", tags=["hods"])

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
    
    expire_holds(db, event_id=event_id)