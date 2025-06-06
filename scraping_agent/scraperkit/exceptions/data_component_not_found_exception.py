
class DataComponentNotFoundException(Exception):
    """
    Exception raised when the target data component is not found; page structure may have changed.
    """
    def __init__(self, message="Target data component not found; page structure may have changed."):
        super().__init__(message)
