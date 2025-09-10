from pydantic import BaseModel, Field
from typing import Optional

"""
BaseModel : it is the base class of Pydantic, so all schemas inherit from it
Field : is used to metadata, like 'title', 'example', and validation like 'ge' and 'le'
Optional : we  use when a field can be 'None' 
"""

class EventBase(BaseModel):
    # Common fields for Event schema
    name: str = Field(..., title="Event name", example="MTV Unplugged")
    total_seats: int = Field(..., title="Total seats", ge=1, example=5)


class EventCreate(EventBase):
    # Schema for creating an event
    pass


class EventRead(EventBase):
    # Schema for reading an event (includes ID)
    id: int

    class Config:
        orm_mode = True 