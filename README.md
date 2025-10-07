# Reservio - Event Reservation System🎸
A seat reservation system.

## 📌 Description
The Reservio project is a seat reservation system for events, and is still under development. Developed with an architecture based on Docker containers to ensure an isolated and consistent environment, the system uses FastAPI to build a RESTful API, SQLAlchemy to manage interaction with the PostgreSQL database, and Pydantic for data validation and serialization.

*Project Status: 🚧 Active Development*

## Features
- Event creation and management
- Seat viewing per event
- Reservation system with secure transactions
- Temporary seat holding (prevents others from reserving while you decide)
- Complete RESTful API with FastAPI
- PostgreSQL database with Docker
- Data validation with Pydantic
- Integration testing with Pytest
- Automatic API documentation (Swagger)
- Isolated testing environment setup
- Modular route and endpoint organization

## 🛠️ Technologies Used
- Backend: **Python, FastAPI**
- Database: **PostgreSQL**
- ORM: **SQLAlchemy**
- Data Validation: **Pydantic**
- Containerization: **Docker, Docker Compose**
- Testing: **Pytest, TestClient**
- Authentication: **JWT** (in progress)
- Deployment: **AWS** (planned)

## 🧪 Testing
``` bash
# Run tests
docker-compose -f docker-compose.test.yml up --build
```
Includes:
- User registration and login tests
- Seat hold and reservation logic

## 📦 Setup & Installation
``` bash
# Clone the repository
git clone https://github.com/gabriel-oligom/reservio.git

# (To be completed) Setup instructions coming soon...