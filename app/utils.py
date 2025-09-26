from datetime import datetime, timezone
from . import models

def expire_holds(db, event_id: int = None):
    """
    Remove expired holds and update seat status to "available"
    """

    # Get current UTC time for comparison
    now = datetime.now(timezone.utc)

    # Query Holds and JOIN Seats to access event_id
    # Filter: select only holds where expiration time (<=) now
    q = db.query(models.Hold).join(models.Seat).filter(models.Hold.expires_at <= now)
    
    # optional filter if event_id is provided
    if event_id:
        q = q.filter(models.Seat.event_id == event_id)
    
    # execute query and fetch all expired holds
    expired = q.all()

    # process expired holds
    for h in expired:
        seat = h.seat
        db.delete(h) # delete hold

        # set seat status  to available only if it was "on_hold"
        if seat and seat.status == "on_hold":
            seat.status = "available"
    if expired:
        db.commit() 