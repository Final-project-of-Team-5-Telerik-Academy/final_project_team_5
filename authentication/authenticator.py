from fastapi import HTTPException
from models.model_user import User
from services.user_service import from_token, is_authenticated


def get_user_or_raise_401(token: str) -> User:
    if not is_authenticated(token):
        raise HTTPException(status_code=401)

    return from_token(token)