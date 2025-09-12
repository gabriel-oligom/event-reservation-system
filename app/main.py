from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models
from .schemas import EventRead, EventCreate
from .database import SessionLocal, engine

"""
Understanding Core Concepts
- HTTPException : used to raise custom HTTP errors with status codes and messages
- status : provides standard HTTP status codes like 201 (Created), 400 (Bad Request), etc
- raise : used to interrupt the flow and throw an error intentionally. Return HTTP errors with custom status codes and messages
- rollback : cancels all changes made during the current database transaction. It helps to avoid saving incomplete or invalid data
- refresh : updates the Python object with the latest data from the database
"""


# Ensure models are registered and tables exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI() # Create the instance of the application

# Opens a DB session for each request and closes it afterwards
def get_db():
    db = SessionLocal()
    try:
        yield db # provides the session for routes that need it
    finally:
        db.close() # and then it closes


@app.get("/")
def root():
    return {"message": "API is working."}


@app.get("/events", response_model=List[EventRead]) # return the data as a list
def read_events(db: Session = Depends(get_db)): # it means that the 'read_events' route depends on 'get_db' to work
    """
    Read-only endpoint: fetch all events from DB
    - db: a variable with SQLAlchemy Session injected by FastAPI (get_db)
    - Session: just a type annotation telling that db is expected to be a SQLAlchemy session
    - Depends: inject dependencies
    - response_model: tells FastAPI/Pydantic to serialize the output using EventRead 
    """
    events = db.query(models.Event).all() # Works like "SELECT * FROM events"
    return events


@app.get("/events/{event_id}", response_model=EventRead, tags=["events"])
def read_event(event_id: int, db: Session = Depends(get_db)):
    """
    Read a single event by its ID
    - event_id: path parameter (FastAPI converts it to 'int')
    - db: SQLAlchemy Session injected via 'Depends(get_db)'
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED, tags=["events"])
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    """
    Create an event and generate the seats
    - event_in: validated input data for the new event (it means that 'event_in' must be an 'EventRead' type of variable)
    - db: SQLAlchemy Session injected by Depends(get_db) 
    """
    # Defensive check
    if not (10 <= event_in.total_seats <= 1000):
        raise HTTPException(status_code=400, detail="total_seats must be between 10 and 1000")
    
    # Create and persist the Event and Seat inside a transaction
    try:
        db_event = models.Event(name=event_in.name, total_seats=event_in.total_seats)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        # Create Seat rows for this event
        seats = []
        for i in range(1, db_event.total_seats + 1):
            seat = models.Seat(number=i, status="available", event_id=db_event.id)
            seats.append(seat)
            db.add(seat)
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        db.rollback() # Undo partial changes
        raise HTTPException(status_code=500, detail="Could not create event") from e
    return db_event