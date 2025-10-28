from __future__ import annotations

from typing import Optional

from flask import current_app
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer


def _get_serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config["SECRET_KEY"]
    salt = current_app.config.get("SECURITY_TOKEN_SALT", "auth-token")
    return URLSafeTimedSerializer(secret_key, salt=salt)


def generate_token(data: dict, purpose: str) -> str:
    serializer = _get_serializer()
    return serializer.dumps({"purpose": purpose, **data})


def validate_token(token: str, purpose: str, max_age: int = 3600) -> Optional[dict]:
    serializer = _get_serializer()
    try:
        data = serializer.loads(token, max_age=max_age)
    except (BadSignature, BadTimeSignature):
        return None
    if data.get("purpose") != purpose:
        return None
    return data
