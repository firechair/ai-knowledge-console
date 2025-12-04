"""
Custom exception classes for the application.

These exceptions provide structured error handling with appropriate HTTP status codes.
"""


class AppException(Exception):
    """Base exception for application errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when input validation fails"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(AppException):
    """Raised when resource not found"""

    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status_code=404)


class ConfigurationError(AppException):
    """Raised when service is not configured"""

    def __init__(self, service: str):
        super().__init__(f"{service} requires configuration", status_code=400)


class ExternalServiceError(AppException):
    """Raised when external API fails"""

    def __init__(self, service: str, details: str = ""):
        message = f"External service {service} failed"
        if details:
            message += f": {details}"
        super().__init__(message, status_code=502)


class RateLimitError(AppException):
    """Raised when rate limit exceeded"""

    def __init__(self):
        super().__init__("Rate limit exceeded", status_code=429)
