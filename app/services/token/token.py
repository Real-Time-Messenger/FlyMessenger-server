import os
from datetime import timedelta, datetime, timezone

import jwt
from fastapi.encoders import jsonable_encoder

from app.models.user.token import TokenInCreateModel


class TokenService:

    @staticmethod
    def generate_access_token(**kwargs) -> str:
        payload = TokenInCreateModel(exp=(datetime.now(tz=timezone.utc) + timedelta(days=30)).timestamp(), iat=datetime.now(tz=timezone.utc).timestamp(), payload=kwargs)
        payload = jsonable_encoder(payload)

        return jwt.encode(payload=payload, key=os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

    @staticmethod
    def decode(token: str) -> dict | None:

        # Create an exception group for jwt exceptions.
        ExceptionGroup = (jwt.InvalidTokenError, jwt.ExpiredSignatureError)  # <-- Only for python 3.11.

        options = {
            "verify_exp": True,  # Verify the expiration time
            "verify_iat": True,  # Verify the issued at time
            "verify_signature": False,  # Verify the signature
        }

        try:
            return jwt.decode(jwt=token, key=os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")],
                              options=options)
        except ExceptionGroup:
            return None

    @staticmethod
    def generate_custom_token(expiration: timedelta, **kwargs) -> str:
        payload = TokenInCreateModel(exp=(datetime.now(tz=None) + expiration).timestamp(), iat=datetime.now(tz=None).timestamp(), payload=kwargs)
        payload = jsonable_encoder(payload)

        return jwt.encode(payload=payload, key=os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

    @staticmethod
    def get_token_expiration(token: str) -> datetime | None:
        decoded_token = TokenService.decode(token)

        if decoded_token is None:
            return None

        return datetime.fromtimestamp(decoded_token.get("exp"), tz=None)
