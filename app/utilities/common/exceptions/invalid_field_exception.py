from core.exceptions import BusinessException, ErrorType


class InvalidFieldException(BusinessException):
    """
    Exception raised when a User is not found
    """

    def __init__(self, field: str = None):
        self.field = field
        self.message = f"{field} format is invalid"
        super().__init__(self.message, error_type=ErrorType.INTERNAL_SERVER_ERROR)
