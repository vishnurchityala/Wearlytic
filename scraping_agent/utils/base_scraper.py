from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, base_url, headers,content_loader=None):
        """
        Initializes the scraper with required parameters.

        Args:
            base_url (str): Base URL of the target site.
            headers (dict): HTTP headers for requests.
            listing_pages (list): List of category/listing page URLs.
            content_loader (BaseContentLoader): An instance to load page content.
        """
        self.base_url = base_url
        self.headers = headers
        self.content_loader = content_loader

        # Will store content of the current page when loaded
        # Buffer storage for data extraction
        self.current_page_content = None
        self.current_product_page_content = None

    @abstractmethod
    def get_pagination_details(self, page_content):
        """
        Extract pagination information from a listing page.

        Args:
            page_content (str): HTML content of the listing page.

        Returns:
            dict: Pagination details (e.g., total pages, current page).
        """
        pass

    @abstractmethod
    def get_product_listings(self, listings_page_url, page):
        """
        Loads and extracts product listings from a category/listing page.

        Args:
            listings_page_url (str): URL of the listing page.
            page (int): Page number for pagination.

        Returns:
            list: List of product dictionaries (e.g., product_id, page_rank, product_link).
        """
        self.current_page_content = self.content_loader.load_content(listings_page_url)
        return self._extract_product_listings(self.current_page_content, page)

    @abstractmethod
    def get_product_details(self, product_page_url):
        """
        Loads and extracts detailed information from a product page.

        Args:
            product_page_url (str): URL of the product page.

        Returns:
            dict: Product details (price, brand, reviews, ratings, etc.).
        """
        self.current_product_page_content = self.content_loader.load_content(product_page_url)
        return self._extract_product_details(self.current_product_page_content)
