"""
Fieldwise AI - Authentication
JWT token management and password hashing
"""

import os
try:
    import bcrypt
except ImportError:
    bcrypt = None
try:
    import jwt
except ImportError:
    jwt = None
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from database import get_user_by_id

SECRET_KEY = os.environ.get("JWT_SECRET", "fieldwise-secret-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(request: Request):
    """Extract and validate user from Authorization header or cookie"""
    token = None

    # Check Authorization header
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]

    # Check cookie fallback
    if not token:
        token = request.cookies.get("fieldwise_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)
    user = get_user_by_id(payload["user_id"])

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_optional_user(request: Request):
    """Return user if authenticated, None otherwise"""
    try:
        return get_current_user(request)
    except HTTPException:
        return None
