
class DriverNotInitializedException(Exception):
    """
    Exception raised when fails to intialize web driver for content loader.
    """
    def __init__(self, message="Exception raised when fails to intialize web driver for content loader."):
        super().__init__(message)