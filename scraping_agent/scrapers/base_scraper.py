from abc import ABC, abstractmethod

"""
BaseScraper is an abstract base class that provides a blueprint for web scrapers.
It defines the essential methods that any scraper class must implement.
"""
class BaseScraper(ABC):
    def __init__(self, base_url, headers=None):
        """
        Initializes the scraper with a base URL and optional headers.
        The headers include default values for User-Agent and Accept-Language to mimic a browser.
        """
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    @abstractmethod
    def get_page_content(self, page_url):
        """
        Abstract method to fetch the content of a web page given its URL.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_pagination_details(self, page_content):
        """
        Abstract method to extract pagination details from the page content.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_product_listings(self, listings_page_url, page=1):
        """
        Abstract method to retrieve product listings from a given page URL.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_product_details(self, product_page_url):
        """
        Abstract method to fetch detailed information about a product from its page URL.
        Must be implemented by subclasses.
        """
        pass