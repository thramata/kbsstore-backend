# utils.py
import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from bson import ObjectId

from config.database import db

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Extract and validate JWT token, return user document.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(401, "Invalid token: missing sub")

    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")

    # Return user doc as-is (auth.py will sanitize before returning)
    return user


def require_admin(user):
    """
    Utility to check for admin privileges.
    """
    if not user or user.get("role") != "admin":
        raise HTTPException(403, "Admin privileges required")
    return True
