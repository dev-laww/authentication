class AppException(Exception):
    code: str = "APP_EXCEPTION"
    """Base exception for the application."""
    pass


class AuthenticationError(AppException):
    """Exception raised for authentication errors."""
    code = "AUTHENTICATION_ERROR"
    pass


class AuthorizationError(AppException):
    """Exception raised for authorization errors."""
    code = "AUTHORIZATION_ERROR"
    pass


class ValidationError(AppException):
    """Exception raised for validation errors."""
    code = "VALIDATION_ERROR"
    pass


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""
    code = "NOT_FOUND_ERROR"
    pass


class DatabaseError(AppException):
    """Exception raised for database-related errors."""
    code = "DATABASE_ERROR"
    pass


class ExternalServiceError(AppException):
    """Exception raised for errors from external services."""
    code = "EXTERNAL_SERVICE_ERROR"
    pass
