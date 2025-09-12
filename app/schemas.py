from pydantic import BaseModel, Field
from typing import Optional

"""
Pydantic: a module that validates and structures data before it's processed or stored in the database
BaseModel : defines the structure and validation rules for data models. It's base class of Pydantic, so all schemas inherit from it
Field : is used to metadata, like 'title', 'example', and validation like 'ge' and 'le'
Optional : we use when a field can be 'None', when is not mandatory
"""

class EventBase(BaseModel):
    # Common fields/structure for Event schema
    name: str = Field(..., title="Event name", example="MTV Unplugged")
    total_seats: int = Field(..., title="Total seats", ge=1, example=5)


class EventCreate(EventBase):
    # Schema for creating an event
    total_seats: int = Field(..., ge=10, le=1000, title="Total seats", example=50)
    pass
 

class EventRead(EventBase):
    # Schema for reading an event (includes ID)
    id: int

    class Config:
        orm_mode = True 


class SeatRead(BaseModel):
    id: int
    number: int = Field(..., Title="Seat number", example=1)
    status: str = Field(..., Title="Seat status", example="available")

    class config:
        orm_mode= True # Allows Pydantic to convert 'models.Seat' (SQLAlchemy model) instances to JSON without manual transformation