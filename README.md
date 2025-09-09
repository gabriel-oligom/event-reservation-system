# Reservio - Event Reservation System🎸
A seat reservation system.

## 📌 Description
The Reservio project is a seat reservation system for events, and is still under development. Developed with an architecture based on Docker containers to ensure an isolated and consistent environment, the system uses FastAPI to build a RESTful API, SQLAlchemy to manage interaction with the PostgreSQL database, and Pydantic for data validation and serialization.

## Features
- Database Creation: Setting up a PostgreSQL database via Docker.
- Model Definition: Creating database models for Events, Seats, and Reservations with SQLAlchemy.
- API Initialization: Setting up a FastAPI server with test endpoints.
- Data Validation: Using Pydantic to validate API input and output schemas.

## 🛠️ Technologies Used
- **PostgreSQL** – Relational database
- **Docker** – Containers for the database
- **FastAPI** – Framework for building the API
- **SQLAlchemy** – ORM for database interaction
- **Pydantic** – Data validation