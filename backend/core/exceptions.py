# core/exceptions.py
"""Custom exceptions for account deletion operations"""

import datetime


class AccountDeletionException(Exception):
    """Base exception for account deletion operations"""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AccountNotFoundException(AccountDeletionException):
    """Raised when account is not found"""

    def __init__(self, email: str | None = None) -> None:
        message = "Účet nebyl nalezen" + (f": {email}" if email else "")
        super().__init__(message, error_code="account_not_found")


class TokenNotFoundException(AccountDeletionException):
    """Raised when deletion token is not found"""

    def __init__(self) -> None:
        super().__init__("Token nenalezen", error_code="token_not_found")


class TokenAlreadyUsedException(AccountDeletionException):
    """Raised when token has already been used"""

    def __init__(self) -> None:
        super().__init__("Token již byl použit", error_code="token_already_used")


class TokenExpiredException(AccountDeletionException):
    """Raised when token has expired"""

    def __init__(self, expires_at: datetime.datetime | None = None) -> None:
        message = "Token vypršel"
        if expires_at:
            message += f" (vypršel: {expires_at.isoformat()})"
        super().__init__(message, error_code="token_expired")


class AccountDeletionFailedException(AccountDeletionException):
    """Raised when account deletion fails"""

    def __init__(self, reason: str | None = None) -> None:
        message = "Chyba při mazání účtu"
        if reason:
            message += f": {reason}"
        super().__init__(message, error_code="deletion_failed")
