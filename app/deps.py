from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWSError
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .utils.security import decode_access_token
from schemas import TokenData

"""
Understanding Core Concepts
- OAuth2AuthorizationCodeBearer: A FastAPI security scheme for OAuth2 authorization code flow; extracts Bearer tokens from HTTP Authorization headers and validates them against a token endpoint (here, "/auth/token")
- JWSError: An exception from the jose library (JWT handling); raised during token decoding if the JWT is malformed, expired, or signature-invalid, caught here to trigger authentication failure
- decode_access_token: A custom utility function (from .utils.security); decodes and verifies a JWT access token, returning its payload (e.g., claims like "sub" for subject/email)
- TokenData: A Pydantic model (from schemas); used to structure validated token payload data, such as the user's email (sub claim), ensuring type safety and validation
- payload: The decoded JWT dictionary containing claims; "sub" is the standard claim for the subject (here, the user's email identifier)
- credentials_exception: A pre-defined HTTPException instance; reused for common auth failures like invalid tokens or missing users, standardizing error responses
"""

oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},
                                          )
    
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except Exception:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user