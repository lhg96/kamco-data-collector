class KamcoError(Exception):
    """Base exception for KAMCO collector."""
    pass

class KamcoApiError(KamcoError):
    """Raised when KAMCO API returns an error or invalid response."""
    pass

class DatabaseError(KamcoError):
    """Raised when database operations fail."""
    pass
