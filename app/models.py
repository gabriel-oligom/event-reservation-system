from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone, timedelta

"""
Understanding the modules and imports
(They are all types and helpers from SQLAlchemy)
- Column : Each attribute of the class turns into a column in the database
- Integer, String : Data types of the columns 
- ForeignKey : Connect different tables
- DateTime : Add a column to store date and/or time
- UniqueConstraint : Ensures that values in one or more columns are unique inside the table
- relationship : Make easier the queries between tables, define relations
- timezone : Use UTC time to avoid timezone headaches across servers
- timedelta : Represent differences between two dates or times (hold duration)
"""

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_seats = Column(Integer, nullable=False)

    # Represents a hierarchical relationship to the Seat class; 
    # access all seats belonging to this event 
    seats = relationship("Seat", back_populates="event")


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="available")
    event_id = Column(Integer, ForeignKey("events.id")) # 'event_id' is a foreign key that references the 'id' column in the 'events' table.

    # Inverse relation to access Event
    event = relationship("Event", back_populates="seats")

    reservation = relationship("Reservation", back_populates="seat", uselist=False) # 'uselist=False' tells SQLAlchemy to return a single object instead of a list

    hold = relationship("Hold", back_populates="seat", uselist=False) # a new relationship, to "Hold"


class Hold(Base):
    __tablename__ = "holds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    seat_id = Column(Integer, ForeignKey("seats.id"), unique=True, nullable=False) # unique : just a single hold for a seat
    held_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    seat = relationship("Seat", back_populates="hold", uselist=False)


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False) 
    seat_id = Column(Integer, ForeignKey("seats.id"), unique=True) # Create an unique index to this column
    reserved_at = Column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc)) # Uses UTC timezone to ensure consistency across different servers and timezones

    seat = relationship("Seat", back_populates="reservation", uselist=False) # sets the current time in UTC when a new reservation is created


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))