"""Domain and application exceptions for Sentinel."""

class SentinelError(Exception):
    """Base Sentinel exception."""
    pass

class BudgetExceededError(SentinelError):
    """Raised when an action would violate the hard $0 budget invariant."""
    pass

class SecurityScanError(SentinelError):
    """Raised when user input contains un-abstracted credentials or connection strings."""
    pass

class ProviderUnavailableError(SentinelError):
    """Raised when an AI provider fails or circuit breaker is open."""
    pass
