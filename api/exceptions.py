from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class CustomAPIException(Exception):
    """Base exception for custom API errors."""
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ValidationError(CustomAPIException):
    """Exception for validation errors."""
    def __init__(self, message):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)

class NotFoundError(CustomAPIException):
    """Exception for not found errors."""
    def __init__(self, message):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class PermissionError(CustomAPIException):
    """Exception for permission errors."""
    def __init__(self, message):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)

def custom_exception_handler(exc, context):
    """Custom exception handler for DRF."""
    response = exception_handler(exc, context)
    
    if response is not None:
        logger.error(f"API Error: {exc.__class__.__name__} - {str(exc)}")
        response.data['status_code'] = response.status_code
        response.data['error_type'] = exc.__class__.__name__
    
    return response