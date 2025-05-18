import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from base_scraper import BaseScraper

"""
MyntraScraper class inherits from BaseScraper and provides methods to scrape Myntra's website.
"""
class MyntraScraper(BaseScraper):
    def __init__(self):
        """
        Initializes the scraper with Myntra's base URL.
        """
        super().__init__("https://www.myntra.com/")
        
    def get_page_content(self, page_url):
        """
        Fetches the HTML content of a given page URL using Selenium.

        Args:
            page_url (str): The URL of the page to fetch.

        Returns:
            str: The HTML content of the page, or None if an error occurs.
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
            chrome_options.add_argument(f"accept-language={self.headers['Accept-Language']}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get(page_url)
            time.sleep(5)
            html_content = driver.page_source
            driver.quit()
            return html_content
        except Exception as e:
            print(f"Error fetching page content from Myntra: {e}")
            return None
    
    def get_pagination_details(self, page_content):
        """
        Extracts pagination details such as current page, total pages, and next page URL from the page content.

        Args:
            page_content (str): The HTML content of the page.

        Returns:
            dict: A dictionary containing pagination details.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        pagination_info = {
            'current_page': None,
            'total_pages': None,
            'next_page_url': None
        }
        try:
            pagination_meta = soup.find('li', {'class': 'pagination-paginationMeta'})
            if pagination_meta:
                meta_text = pagination_meta.text.strip()
                if 'Page' in meta_text and 'of' in meta_text:
                    parts = meta_text.split()
                    if len(parts) >= 4:
                        current_page = int(parts[1])
                        total_pages = int(parts[3])
                        pagination_info['current_page'] = current_page
                        pagination_info['total_pages'] = total_pages
                        canonical = soup.find('link', {'rel': 'canonical'})
                        current_url = ""
                        if canonical and 'href' in canonical.attrs:
                            current_url = canonical['href']
                        else:
                            meta_url = soup.find('meta', {'property': 'og:url'})
                            if meta_url and 'content' in meta_url.attrs:
                                current_url = meta_url['content']
                        if current_url and current_page < total_pages:
                            import re
                            if 'p=' in current_url:
                                next_url = re.sub(r'p=\d+', f'p={current_page + 1}', current_url)
                            else:
                                if '?' in current_url:
                                    next_url = f"{current_url}&p={current_page + 1}"
                                else:
                                    next_url = f"{current_url}?p={current_page + 1}"
                            pagination_info['next_page_url'] = next_url
            return pagination_info
        except Exception as e:
            print(f"Error extracting pagination details: {e}")
            return pagination_info

    def get_product_listings(self, listings_page_url, page=1):
        """
        Retrieves product listing URLs from a given page.

        Args:
            listings_page_url (str): The URL of the listings page.
            page (int): The page number to fetch.

        Returns:
            list: A list of product URLs.
        """
        if page > 1:
            if '?' in listings_page_url:
                url = f"{listings_page_url}&p={page}"
            else:
                url = f"{listings_page_url}?p={page}"
        else:
            url = listings_page_url
        page_content = self.get_page_content(url)
        if not page_content:
            print(f"Failed to retrieve content for page {page}")
            return []
        soup = BeautifulSoup(page_content, 'html.parser')
        product_links = []
        product_items = soup.find_all('li', class_='product-base')
        for item in product_items:
            product_id = item.get('id')
            a_tag = item.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = 'https://www.myntra.com/' + href.lstrip('/')
                if full_url not in product_links:
                    product_links.append(full_url)
        print(f"Found {len(product_links)} unique product links on page {page}")
        return product_links

    def extract_colors(self, soup):
        """
        Extracts available color options from the product page.

        Args:
            soup (BeautifulSoup): The parsed HTML content of the product page.

        Returns:
            list: A list of color names.
        """
        color_names = []
        color_names= [a["title"] for a in soup.select(".colors-container a") if a.has_attr("title")]
        return color_names

    def get_product_details(self, product_page_url):
        """
        Extracts detailed information about a product from its page.

        Args:
            product_page_url (str): The URL of the product page.

        Returns:
            dict: A dictionary containing product details such as title, brand, price, rating, sizes, colors, and images.
        """
        try:
            page_content = self.get_page_content(product_page_url)
            if not page_content:
                print(f"Failed to retrieve content for product page: {product_page_url}")
                return {}
            soup = BeautifulSoup(page_content, 'html.parser')
            product_details = {
                'url': product_page_url,
                'source': 'Myntra'
            }
            product_name = soup.find('h1', {'class': 'pdp-name'})
            if product_name:
                product_details['title'] = product_name.text.strip()
            brand_name = soup.find('h1', {'class': 'pdp-title'})
            if brand_name:
                product_details['brand'] = brand_name.text.strip()
            price = soup.find('span', {'class': 'pdp-price'})
            if price:
                product_details['price'] = price.text.strip()[1:]
            rating = soup.find('div', {'class': 'index-overallRating'})
            if rating:
                product_details['rating'] = rating.text.strip().split("|")[0]
                product_details['rating_count'] = rating.text.strip().split("|")[1].split()[0]
            description = soup.find('div', {'class': 'pdp-product-description-content'})
            if description:
                product_details['description'] = description.text.strip()
            sizes = []
            size_buttons = soup.find_all('div', {'class': 'size-buttons-size-button'})
            for size_button in size_buttons:
                size_text = size_button.text.strip()
                if size_text:
                    sizes.append(size_text)
            if sizes:
                product_details['available_sizes'] = sizes
            colors = [a["title"] for a in soup.select(".colors-container a") if a.has_attr("title")]
            if colors:
                product_details['colors'] = colors
            specifications = description = soup.select_one(".pdp-product-description-content").get_text(separator=" ", strip=True)
            if specifications:
                product_details['description'] = specifications
            images = []
            image_containers = soup.find_all('div', {'class': 'image-grid-image'})
            for img_container in image_containers:
                img_tag = img_container.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    images.append(img_tag['src'])
            if images:
                product_details['images'] = images
            return product_details
        except Exception as e:
            print(f"Error extracting product details: {e}")
            return {}

if __name__ == "__main__":
    """
    Main execution block to test the scraper functionality.
    """
    scraper = MyntraScraper()
    search_url = "https://www.myntra.com/tshirts"
    html_content = scraper.get_page_content(search_url)
    if html_content:
        print(f"Successfully retrieved {len(html_content)} characters of HTML")
        with open("myntra_results.html", "w+", encoding="utf-8") as file:
            file.write(html_content)
        pagination_details = scraper.get_pagination_details(html_content)
        print("\nPagination Details:")
        for key, value in pagination_details.items():
            print(f"{key}: {value}")
        product_links = scraper.get_product_listings(search_url)
        print("\nSample Product Links:")
        for i, link in enumerate(product_links):
            print(f"{i+1}. {link}")
        product_url = product_links[-1]
        product_details = scraper.get_product_details(product_url)
        print("\nProduct Details:")
        for key, value in product_details.items():
            print(f"{key}: {value}")
    else:
        print("Failed to retrieve content")
