import hashlib
import secrets
from datetime import datetime, timedelta
from typing import TypedDict

from core.exceptions import TokenAlreadyUsedException, TokenExpiredException
from core.models import AccountDeletionToken


class TokenResponse(TypedDict):
    hash_token: str
    plain_token: str


class TokenGenerator:
    """Token generation and validation for account deletion"""

    TOKEN_EXPIRY_HOURS = 24
    TOKEN_BYTES = 32  # 256 bits of entropy

    @staticmethod
    def generate_deletion_token() -> str:
        """
        Generate cryptographically secure token (256 bits of entropy).

        Returns:
            URL-safe base64 encoded token string (43 characters)

        Example output: 'xB9j3K_mNpQ2rL8vT5wY1hF6dS4cA7eU9iO0gH3kZ2x'
        """
        return secrets.token_urlsafe(TokenGenerator.TOKEN_BYTES)

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash token for secure database storage using SHA-256.

        Args:
            token: Plain text token to hash

        Returns:
            Hexadecimal string representation of SHA-256 hash (64 characters)

        Example:
            Input:  'xB9j3K_mNpQ2rL8vT5wY1hF6dS4cA7eU9iO0gH3kZ2x'
            Output: 'a1b2c3d4e5f6...xyz' (64 hex chars)
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def get_expiration_time(hours: int = TOKEN_EXPIRY_HOURS) -> datetime:
        """
        Calculate token expiration timestamp.

        Args:
            hours: Number of hours until token expires (default 24)

        Returns:
            datetime object representing expiration time

        Example:
            If current time is 2025-10-18 10:00:00
            get_expiration_time(24) returns 2025-10-19 10:00:00
        """
        return datetime.utcnow() + timedelta(hours=hours)

    @staticmethod
    def validate_token(token_record: AccountDeletionToken) -> None:
        """
        Validate deletion token against business rules.

        Args:
            token_record: AccountDeletionToken record from database or None

        Raises:
            TokenAlreadyUsedException: If token was already used
            TokenExpiredException: If token has expired

        Validation checks:
            1. Token exists in database
            2. Token hasn't been used yet
            3. Token hasn't expired
        """

        if token_record.used_at:
            raise TokenAlreadyUsedException()

        if datetime.utcnow() > token_record.expires_at:
            raise TokenExpiredException(expires_at=token_record.expires_at)

    @staticmethod
    def generate_and_hash() -> TokenResponse:
        """
        Convenience method to generate token and its hash in one call.

        Returns:
            TokenResponse dict with plain_token and hash_token

        Example:
            result = TokenGenerator.generate_and_hash()
            # result['plain_token']:  'xB9j3K_mNpQ2rL8vT5wY1hF6dS4cA7eU9iO0gH3kZ2x'
            # result['hash_token']: 'a1b2c3d4e5f6...xyz'
        """
        plain_token = TokenGenerator.generate_deletion_token()
        token_hash = TokenGenerator.hash_token(plain_token)
        return TokenResponse(plain_token=plain_token, hash_token=token_hash)
