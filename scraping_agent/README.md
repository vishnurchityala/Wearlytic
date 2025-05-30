## `ScrapingAgent`

The `ScrapingAgent` provides a unified API for extracting product data at scale from multiple sources across different websites. It serves as an abstraction layer to standardize and streamline the scraping process, regardless of the underlying site-specific implementations.

## `BaseContentLoader` Class
The `BaseContentLoader` is an abstract base class that defines a common interface for implementing various strategies to load different types of web pages. It also provides the flexibility to create custom page loaders using any available library or technology.

```[python]
from abc import ABC, abstractmethod

class BaseContentLoader(ABC):
    def __init__(self, headers):
        """
        Initializes the content loader with HTTP headers.

        Args:
            headers (dict): HTTP headers to use for the request.
        """
        self.headers = headers

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
```

## `BaseScraper` Class

The `BaseScraper` is an abstract base class designed to provide a common interface for implementing web scrapers across different websites. Subclasses can implement their own scraping logic using the most suitable libraries and techniques for the target site, ensuring optimal performance and flexibility.


``` [python]
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, base_url, headers, listing_pages, content_loader):
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
        self.listing_pages = listing_pages
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

```