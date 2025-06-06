
class RateLimitException(Exception):
    """
    Exception raised when the target page has been accessed too frequently, triggering rate limiting.
    """
    def __init__(self, message="The target page has been accessed too frequently, triggering rate limiting."):
        super().__init__(message)
