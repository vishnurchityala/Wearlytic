from abc import ABC, abstractmethod

class BaseContentLoader(ABC):
    def __init__(self, headers=None):
        """
        Initializes the content loader with HTTP headers.

        Args:
            headers (dict): HTTP headers to use for the request.
        """
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }


    @abstractmethod
    def load_content(self, page_url):
        """
        Loads content from the specified page URL.

        Args:
            page_url (str): The URL of the page to scrape data from.

        Returns:
            str: The raw content of the page.
        """
        pass