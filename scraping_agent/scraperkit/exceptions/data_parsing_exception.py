
class DataParsingException(Exception):
    """
    Exception raised when a data type error occurs while parsing the extracted data.
    """
    def __init__(self, message="Encountered a data type error while parsing the extracted data."):
        super().__init__(message)
