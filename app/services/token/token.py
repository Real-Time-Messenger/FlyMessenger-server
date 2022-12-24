import os
from datetime import timedelta, datetime, timezone
from typing import Any, Optional

import jwt
from fastapi.encoders import jsonable_encoder

from app.models.user.token import TokenInCreateModel


class TokenService:
    """
    Service for working with tokens.

    This class allows us to work with tokens.
    """

    @staticmethod
    def generate_access_token(**kwargs: Any) -> str:
        """
        Generate access token.

        :param kwargs: Token data.

        :return: Access token.
        """

        payload = TokenInCreateModel(exp=(datetime.now(tz=timezone.utc) + timedelta(days=30)).timestamp(),
                                     iat=datetime.now(tz=timezone.utc).timestamp(), payload=kwargs)
        payload = jsonable_encoder(payload)

        return jwt.encode(payload=payload, key=os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

    @staticmethod
    def decode(token: str) -> Optional[dict]:
        """
        Decode token.

        :param token: Token.

        :return: Decoded token.
        """
        options = {
            "verify_exp": True,         # Verify the expiration time
            "verify_iat": True,         # Verify the issued at time
            "verify_signature": False,  # Verify the signature
        }

        try:
            return jwt.decode(jwt=token, key=os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")],
                              options=options)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def generate_custom_token(
            expiration: timedelta,
            **kwargs: Any
    ) -> str:
        """
        Generate custom token.

        :param expiration: Token expiration time.
        :param kwargs: Token data.

        :return: Custom token.
        """

        payload = TokenInCreateModel(exp=(datetime.now(tz=None) + expiration).timestamp(),
                                     iat=datetime.now(tz=None).timestamp(), payload=kwargs)
        payload = jsonable_encoder(payload)

        return jwt.encode(payload=payload, key=os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

    @staticmethod
    def get_token_expiration(token: str) -> Optional[datetime]:
        """
        Get token expiration time.

        :param token: Token.

        :return: Token expiration time.
        """

        decoded_token = TokenService.decode(token)

        if decoded_token is None:
            return None

        return datetime.fromtimestamp(decoded_token.get("exp"), tz=None)
