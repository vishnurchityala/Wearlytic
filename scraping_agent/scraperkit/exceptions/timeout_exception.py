
class TimeoutException(Exception):
    """
    Exception raised when page content takes too long to load and exceeds the allowed time limit.
    """
    def __init__(self, message="Page content took too long to load and exceeded the allowed time limit."):
        super().__init__(message)