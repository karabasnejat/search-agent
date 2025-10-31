"""Domain exceptions."""


class DomainException(Exception):
    """Base exception for domain layer."""
    pass


class RepositoryException(DomainException):
    """Exception raised by repository implementations."""
    pass


class EntityValidationException(DomainException):
    """Exception raised when entity validation fails."""
    pass
