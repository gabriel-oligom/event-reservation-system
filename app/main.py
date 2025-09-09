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
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "API is working."}


@app.get("/events", response_model=List[schemas.EventRead])
def read_events(db: Session = Depends(get_db)):
    """
    Read-only endpoint: fetch all events from DB
    - db: a SQLAlchemy Session injected by FastAPI (get_db)
    - Depends: inject dependencies
    - response_model: tells FastAPI/Pydantic to serialize the output using EventRead 
    """
    events = db.query(models.Event).all() # Works like "SELECT * FROM events"
    return events