from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

"""
Pydantic: a module that validates and structures data before it's processed or stored in the database
BaseModel : defines the structure and validation rules for data models. It's base class of Pydantic, so all schemas inherit from it
Field : is used to metadata, like 'title', 'example', and validation like 'ge' and 'le'
Optional : we use when a field can be 'None', when is not mandatory
datetime : used as a timestamp to know when a reservation was created
EmailStr : a Pydantic type that ensures the value is a valid email format
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
    number: int = Field(..., title="Seat number", example=1)
    status: str = Field(..., title="Seat status", example="available")

    class config:
        orm_mode= True # allows Pydantic to convert 'models.Seat' (SQLAlchemy model) instances to JSON without manual transformation


class ReservationCreate(BaseModel): # input schema (defines which data the client must provide to create a reservation)
    user_id: str = Field(..., title="User UUID", example="123e4567-e89b-12d3-a456-426614174000")


class ReservationRead(BaseModel): # output schema (defines which data is returned to the client)
    id: int
    user_id: str
    seat_id: int
    reserved_at: datetime

    class config:
        orm_mode = True


class ReservationCancel(BaseModel): # schema for reservation cancellation request, identifying the user by UUID.
    user_id: str = Field(..., title="User UUID", example="123e4567-e89b-12d3-a456-426614174000")


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class config:
        orm_mode = True


class Token(BaseModel): # schema for login response (JWT token format)
    access_token: str
    token_type: str


class TokenData(BaseModel): # internal structure used when decoding JWT token
    email: Optional[str]= None