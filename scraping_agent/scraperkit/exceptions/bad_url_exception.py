
class BadURLException(Exception):
    """
    Exception raised when an invalid or malformed URL is provided for scraping.
    """
    def __init__(self, message="Invalid or malformed URL provided for scraping."):
        super().__init__(message)
