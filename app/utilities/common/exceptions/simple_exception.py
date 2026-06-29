from core.exceptions.exceptions import BusinessException

from core.exceptions.exceptions import ErrorType


class SimpleException(BusinessException):
    """
    Simple Exception raised whith a message
    """

    def __init__(self, message: str = None, error_type: ErrorType = ErrorType.INTERNAL_SERVER_ERROR):
        self.message = message
        self.message = f"{message}"
        super().__init__(self.message, error_type=error_type)
