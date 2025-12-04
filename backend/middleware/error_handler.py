"""
Error handling middleware and exception handlers for FastAPI.

Provides centralized error handling with structured logging and consistent error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from exceptions import AppException
import logging
import traceback

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handler middleware.
    
    Catches all exceptions during request processing and returns structured error responses.
    """
    try:
        return await call_next(request)
    except AppException as e:
        logger.warning(
            f"Application error: {e.message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": e.status_code,
            },
        )
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.message, "type": e.__class__.__name__},
        )
    except Exception as e:
        logger.error(
            f"Unhandled error: {str(e)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc(),
            },
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "An unexpected error occurred",
                "type": "InternalServerError",
            },
        )


def register_exception_handlers(app):
    """
    Register custom exception handlers with the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle custom application exceptions"""
        logger.warning(f"Application error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "type": exc.__class__.__name__},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled error: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "An unexpected error occurred",
                "type": "InternalServerError",
            },
        )
