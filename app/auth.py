from secrets import token_urlsafe
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer()


# Demo-only user store.
# In production, passwords should be hashed and stored in a real database.
DEMO_USERS = {
    "low@project.com": {
        "password": "lowpass"
    },
    "medium@project.com": {
        "password": "mediumpass"
    },
    "high@project.com": {
        "password": "highpass"
    }
}


# Demo-only in-memory token store.
# Format: generated_token -> user_email
ACTIVE_TOKENS = {}


def authenticate_user(email: str, password: str) -> bool:
    user = DEMO_USERS.get(email)

    if not user:
        return False

    return user["password"] == password


def create_access_token(email: str) -> str:
    token = token_urlsafe(32)
    ACTIVE_TOKENS[token] = email
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials

    if token not in ACTIVE_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

    return ACTIVE_TOKENS[token]