## `ScrapingAgent`

The `ScrapingAgent` provides a unified API for extracting product data at scale from multiple sources across different websites. It serves as an abstraction layer to standardize and streamline the scraping process, regardless of the underlying site-specific implementations.


## `BaseScraper` Class

The `BaseScraper` is an abstract base class designed to provide a common interface for implementing web scrapers across different websites. Subclasses can implement their own scraping logic using the most suitable libraries and techniques for the target site, ensuring optimal performance and flexibility.


``` [python]
class BaseScraper(ABC):

    def __init__(self, base_url, headers, listing_pages):
        self.base_url = base_url
        self.headers = headers
        self.listing_pages = listing_pages

    
    @abstractmethod
    def get_pagination_details(self, page_content):
        """
        Extract pagination information from a listing page
        
        Args:
            page_content: The page content to extract pagination info from
            
        Returns:
            Dictionary with pagination details (total pages, current page, etc.)
        """
        pass

    @abstractmethod
    def get_product_listings(self, listings_page_url, page):

        """
        Extract product listings from a category/listing page
        
        Arguments:
            listings_page_url: URL of the category/listing page
            page: Page number for pagination
            
        Returns:
            List of product dictionaries with basic info (product_id,page_rank) and links
        """
        pass

    @abstractmethod
    def get_product_details(self,product_page_url):
        
        """
        Extract detailed information from a product page
        Arguments:
            product_page_url: URL of the product detail page
            
        Returns:
            Dictionary containing all product details (price, brand, reviews, ratings, etc.)
        """
        pass
```
