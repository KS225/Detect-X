class EmailAlreadyExistsException(Exception):
    """Raised when a user tries to register with an existing email."""
    pass


class InvalidCredentialsException(Exception):
    """Raised when login credentials are invalid."""
    pass