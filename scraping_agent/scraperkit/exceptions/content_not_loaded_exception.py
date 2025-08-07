
class ContentNotLoadedException(Exception):
    """
    Exception raised when unable to load the content from the specified page URL.
    """
    def __init__(self, message="Unable to load the content from the specified page URL."):
        super().__init__(message)
