from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

"""
Understanding the modules and imports
- Column : Each attribute of the class turns into a column in the database
- Integer, String : Data types of the columns 
- ForeignKey : Connect different tables
- relationship : Make easier the queries between tables, define relations
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