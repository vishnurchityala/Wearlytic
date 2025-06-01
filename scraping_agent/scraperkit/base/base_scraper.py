from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, base_url: str, headers: dict = None, content_loader = None):
        """
        Initializes the scraper with required parameters.

        Args:
            base_url (str): Base URL of the target site.
            headers (dict, optional): HTTP headers for requests.
            content_loader: An instance to load page content.
        """
        self.base_url = base_url
        self.headers = headers
        self.content_loader = content_loader

        # Will store content of the current page when loaded
        # Buffer storage for data extraction
        self.current_page_content = None
        self.current_product_page_content = None

    @abstractmethod
    def get_page_content(self, page_url: str) -> str | None:
        """
        Loads the content of a page.

        Args:
            page_url (str): URL of the page to load.

        Returns:
            str | None: HTML content of the page or None if loading fails.
        """
        pass

    @abstractmethod
    def get_pagination_details(self, page_url: str) -> dict:
        """
        Extract pagination information from a listing page.

        Args:
            page_url (str): URL of the listing page.

        Returns:
            dict: Pagination details containing:
                - current_page (int): Current page number
                - total_pages (int): Total number of pages
                - next_page_url (str): URL of the next page
        """
        pass

    @abstractmethod
    def get_product_listings(self, listings_page_url: str, page: int = 1) -> list[str]:
        """
        Loads and extracts product listings from a category/listing page.

        Args:
            listings_page_url (str): URL of the listing page.
            page (int, optional): Page number for pagination. Defaults to 1.

        Returns:
            list[str]: List of product URLs.
        """
        pass

    @abstractmethod
    def get_product_details(self, product_page_url: str) -> dict:
        """
        Loads and extracts detailed information from a product page.

        Args:
            product_page_url (str): URL of the product page.

        Returns:
            dict: Product details dictionary.
        """
        pass

    def close(self):
        """
        Cleanup method to close any open resources.
        Should be called when the scraper is no longer needed.
        """
        if self.content_loader:
            self.content_loader.close()
