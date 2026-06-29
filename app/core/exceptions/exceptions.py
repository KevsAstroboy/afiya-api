from enum import Enum
from typing import Optional, Any


class ErrorType(Enum):
    """
    Standardized error types for API responses
    """
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class BusinessException(Exception):
    """
    Base exception for all business logic errors
    Provides a standardized way to handle and serialize errors
    """

    def __init__(
            self,
            message: str,
            error_type: ErrorType = ErrorType.INTERNAL_SERVER_ERROR,
            details: Optional[Any] = None
    ):
        """
        Initialize a business exception

        :param message: Human-readable error message
        :param error_type: Standardized error type
        :param details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details

    def to_dict(self):
        """
        Convert exception to a dictionary for API response

        :return: Standardized error response dictionary
        """
        return {
            "message": self.message,
            "error_type": self.error_type.value,
            "details": self.details
        }
