from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

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

    def _extract_id(self, soup: BeautifulSoup) -> str:
        """
        Extracts the unique product ID from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            str: Product ID.
        """
        pass

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extracts the product title from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            str: Product title.
        """
        pass

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """
        Extracts the product category from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            str: Product category.
        """
        pass

    def _extract_price(self, soup: BeautifulSoup) -> float:
        """
        Extracts the product price from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            float: Product price.
        """
        pass

    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        """
        Extracts available sizes for the product from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            list: List of available sizes.
        """
        pass

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """
        Extracts the product description from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            str: Product description.
        """
        pass

    def _extract_material(self, soup: BeautifulSoup) -> str:
        """
        Extracts the material information of the product from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            str: Product material.
        """
        pass

    def _extract_image_url(self, soup: BeautifulSoup) -> list:
        """
        Extracts image URLs for the product from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            list: List of image URLs.
        """
        pass

    def _extract_gender(self, soup: BeautifulSoup) -> str:
        """
        Extracts the gender category of the product from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            str: Gender category.
        """
        pass

    def _extract_colors(self, soup: BeautifulSoup) -> list:
        """
        Extracts available colors for the product from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            list: List of available colors.
        """
        pass

    def _extract_rating(self, soup: BeautifulSoup) -> float:
        """
        Extracts the product rating from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            float: Product rating.
        """
        pass

    def _extract_review_count(self, soup: BeautifulSoup) -> int:    
        """
        Extracts the number of reviews for the product from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML of the product page.

        Returns:
            int: Number of reviews.
        """
        pass

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
            dict: Product details dictionary including page_content.
        """
        pass

    def close(self):
        """
        Cleanup method to close any open resources.
        Should be called when the scraper is no longer needed.
        """
        if self.content_loader:
            self.content_loader.close()
