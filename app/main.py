from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import SessionLocal, engine

# Ensure models are registered and tables exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI() # Create the instance of the application

# Opens a DB session for each request and closes it afterwards
def get_db():
    db = SessionLocal()
    try:
        yield db # provides the session for routes that need it
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "API is working."}


@app.get("/events", response_model=List[schemas.EventRead]) # return the data as a list
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