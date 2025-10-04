from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from .. import models
from ..schemas import UserCreate, UserRead, Token, TokenData
from ..database import get_db
from ..utils.security import verify_password, get_password_hash, create_access_token, decode_access_token
import os

"""
Understanding Core Concepts
- status : provides standard HTTP status codes like 201 (Created), 400 (Bad Request), etc
- Depends : used for Dependency Injection, typically to inject a database session (get_db) or token data
- OAuth2PasswordRequestForm : a utility class provided by FastAPI to handle user authentication via username and password form data
- OAuth2PasswordBearer : a utility class used to define the security scheme (Bearer token) and extract the token from the request header
- timedelta : used to calculate time differences, typically to set the expiration time for the access token
- Token : a Pydantic schema used to structure the JWT (JSON Web Token) response (access_token, token_type)
- TokenData : a Pydantic schema used to structure the payload (data stored) inside the JWT
- create_access_token : a function used to generate the new, signed access token
- decode_access_token : a function used to verify the signature of the token and extract the data
"""

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user and adds them to the database
    - user_in: Body parameter with email and password (UserCreate schema)
    - db: SQLAlchemy Session injected by Depends(get_db)
    - raises 400 if email is already registered
    """
    # check existing
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = get_password_hash(user_in.password)
    
    user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT access token
    - form_data: Standard OAuth2 login form data (username=email, password)
    - db: SQLAlchemy Session injected by Depends(get_db)
    - Returns: Access token and token type (bearer)
    - raises 400 for incorrect email or password
    """
    # OAuth2PasswordRequestForm has attributes: username, password
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
   
    access_token_expires = timedelta (minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}