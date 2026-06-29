from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions.exceptions import BusinessException, ErrorType


def setup_global_exception_handler(app: FastAPI):
    """
    Set up a global exception handler for business exceptions

    :param app: FastAPI application instance
    """

    @app.exception_handler(BusinessException)
    async def business_exception_handler(
            request: Request,
            exc: BusinessException
    ):
        """
        Handle all business exceptions with a standardized response

        :param request: Incoming HTTP request
        :param exc: Raised business exception
        :return: Standardized JSON response
        """
        status_code_map = {
            ErrorType.NOT_FOUND: 404,
            ErrorType.ALREADY_EXISTS: 409,
            ErrorType.VALIDATION_ERROR: 400,
            ErrorType.UNAUTHORIZED: 401,
            ErrorType.FORBIDDEN: 403,
            ErrorType.INTERNAL_SERVER_ERROR: 500
        }

        status_code = status_code_map.get(
            exc.error_type,
            500  # Default to internal server error
        )

        return JSONResponse(
            status_code=status_code,
            content=exc.to_dict()
        )