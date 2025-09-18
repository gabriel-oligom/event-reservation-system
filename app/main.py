from fastapi import FastAPI
from . import models
from .database import SessionLocal, engine
from .routers import events, seats, reservations

# Ensure models are registered and tables exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI() # Create the instance of the application

app.include_router(events.router)
app.include_router(seats.router)
app.include_router(reservations.router_seat)
app.include_router(reservations.router_event)

@app.get("/")
def root():
    return {"message": "API is working."}