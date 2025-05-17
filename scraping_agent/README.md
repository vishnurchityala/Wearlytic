## `ScrapingAgent`

The `ScrapingAgent` provides a unified API for extracting product data at scale from multiple sources across different websites. It serves as an abstraction layer to standardize and streamline the scraping process, regardless of the underlying site-specific implementations.


## `BaseScraper` Class

The `BaseScraper` is an abstract base class designed to provide a common interface for implementing web scrapers across different websites. Subclasses can implement their own scraping logic using the most suitable libraries and techniques for the target site, ensuring optimal performance and flexibility.


``` [python]
class BaseScraper(ABC):

    def __init__(self, base_url):
        self.base_url = base_url
    
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

The `AmazonScraper` a sample implementation of `BaseScraper` class.

```
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import BaseScraper
class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.amazon.in/")
        
    def get_page_content(self, page_url):
        try:
            chrome_options = Options()
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
            chrome_options.add_argument(f"accept-language={self.headers['Accept-Language']}")
            
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.get(page_url)
            
            time.sleep(3)
            
            html_content = driver.page_source
            
            driver.quit()
            
            return html_content
            
        except Exception as e:
            print(f"Error fetching page content: {e}")
            return None
    
    def get_pagination_details(self, page_content):
        soup = BeautifulSoup(page_content, 'html.parser')
        pagination_info = {
            'current_page': None,
            'total_pages': None,
            'next_page_url': None
        }

        current_page_tag = soup.find('span', {'class': 's-pagination-item s-pagination-selected'})
        if current_page_tag and current_page_tag.text.isdigit():
            pagination_info['current_page'] = int(current_page_tag.text)

        page_numbers = soup.find_all('span', {'class': 's-pagination-item'})
        page_nums = []
        for page in page_numbers:
            try:
                num = int(page.text)
                page_nums.append(num)
            except ValueError:
                continue
        if page_nums:
            pagination_info['total_pages'] = max(page_nums)

        next_page_tag = soup.find('a', {'class': 's-pagination-next'})
        if next_page_tag and 'href' in next_page_tag.attrs:
            pagination_info['next_page_url'] = 'https://www.amazon.in' + next_page_tag['href']

        return pagination_info
    
    def get_product_listings(self, listings_page_url, page=1):
        if page > 1:
            if '?' in listings_page_url:
                url = f"{listings_page_url}&page={page}"
            else:
                url = f"{listings_page_url}?page={page}"
        else:
            url = listings_page_url
            
        page_content = self.get_page_content(url)
        
        if not page_content:
            print(f"Failed to retrieve content for page {page}")
            return []
            
        soup = BeautifulSoup(page_content, 'html.parser')
        product_links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/dp/' in href:
                asin_start = href.find('/dp/') + 4
                asin_end = href.find('/', asin_start) if href.find('/', asin_start) > 0 else len(href)
                asin = href[asin_start:asin_end]
                
                product_url = f"https://www.amazon.in/dp/{asin}"
                
                if product_url not in product_links:
                    product_links.append(product_url)
        
        print(f"Found {len(product_links)} unique product links on page {page}")
        return product_links
    
    def get_product_details(self, product_page_url):
        try:
            page_content = self.get_page_content(product_page_url)
            if not page_content:
                print(f"Failed to retrieve content for product page: {product_page_url}")
                return {}

            soup = BeautifulSoup(page_content, 'html.parser')
            product_details = {}

            title_tag = soup.find('span', {'id': 'productTitle'})
            if title_tag:
                product_details['title'] = title_tag.text.strip()

            price_tag = soup.find('span', {'id': 'priceblock_ourprice'})
            if not price_tag:
                price_tag = soup.find('span', {'id': 'priceblock_dealprice'})
            if price_tag:
                product_details['price'] = price_tag.text.strip()

            rating_tag = soup.find('span', {'class': 'a-icon-alt'})
            if rating_tag:
                product_details['rating'] = rating_tag.text.strip()

            review_count_tag = soup.find('span', {'id': 'acrCustomerReviewText'})
            if review_count_tag:
                product_details['review_count'] = review_count_tag.text.strip()

            return product_details

        except Exception as e:
            print(f"Error fetching product details: {e}")
            return {}
```
