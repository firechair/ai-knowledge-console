"""
Logging configuration for structured JSON logging.

Provides JSON-formatted logging for production environments, making logs
easily parseable by log aggregators like Elasticsearch, Datadog, or CloudWatch.
"""

import logging
import sys
import uuid
from typing import Optional
from pythonjsonlogger import jsonlogger


def setup_logging(app_name: str = "ai-knowledge-console", level: str = "INFO") -> logging.Logger:
    """
    Configure structured JSON logging for the application.
    
    Args:
        app_name: Application name for log identification
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Configured root logger
    
    Example:
        >>> logger = setup_logging(level="DEBUG")
        >>> logger.info("Application started")
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger"
        }
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Add app name to all logs
    logging.getLogger().addFilter(
        lambda record: setattr(record, 'app', app_name) or True
    )
    
    return logger


class RequestLogger:
    """
    Context-aware logger for HTTP requests.
    
    Provides request-scoped logging with automatic request ID tracking,
    path, method, and timing information.
    
    Attributes:
        logger: Python logger instance
        request_id: Unique identifier for the request
        path: Request URL path
        method: HTTP method (GET, POST, etc.)
    
    Example:
        >>> req_logger = RequestLogger(
        ...     request_id="abc-123",
        ...     path="/api/chat",
        ...     method="POST"
        ... )
        >>> req_logger.log_info("Processing request", user_id=42)
    """
    
    def __init__(self, request_id: str, path: str, method: str):
        """
        Initialize request logger.
        
        Args:
            request_id: Unique identifier for this request
            path: Request URL path
            method: HTTP method
        """
        self.logger = logging.getLogger(__name__)
        self.request_id = request_id
        self.path = path
        self.method = method
    
    def log_info(self, message: str, **kwargs):
        """
        Log info level message with request context.
        
        Args:
            message: Log message
            **kwargs: Additional structured data to include in log
        """
        self.logger.info(
            message,
            extra={
                'request_id': self.request_id,
                'path': self.path,
                'method': self.method,
                **kwargs
            }
        )
    
    def log_warning(self, message: str, **kwargs):
        """
        Log warning level message with request context.
        
        Args:
            message: Log message
            **kwargs: Additional structured data to include in log
        """
        self.logger.warning(
            message,
            extra={
                'request_id': self.request_id,
                'path': self.path,
                'method': self.method,
                **kwargs
            }
        )
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """
        Log error level message with request context and exception details.
        
        Args:
            message: Log message
            error: Optional exception to include details from
            **kwargs: Additional structured data to include in log
        """
        extra = {
            'request_id': self.request_id,
            'path': self.path,
            'method': self.method,
            **kwargs
        }
        
        if error:
            extra['error_type'] = type(error).__name__
            extra['error_message'] = str(error)
            # Include traceback if available
            import traceback
            extra['traceback'] = traceback.format_exc()
        
        self.logger.error(message, extra=extra)
