import time
from bs4 import BeautifulSoup
from scraperkit.base.base_scraper import BaseScraper
from scraperkit.loaders.selenium_content_loader import SeleniumContentLoader
from scraperkit.models.product import Product
from datetime import datetime, timezone

class MyntraScraper(BaseScraper):
    """
    MyntraScraper implementation of BaseScraper, scraping Amazon.in product info.
    """
    def __init__(self, headers=None):
        super().__init__("https://www.myntra.com/", headers=headers)
        self.id_prefix = "mynt_"
        self.content_loader = SeleniumContentLoader(headers=headers)

    def get_page_content(self, page_url: str) -> str | None:
        try:
            return self.content_loader.load_content(page_url)
        except Exception as e:
            print(f"Error fetching page content from Myntra: {e}")
            return None

    def get_pagination_details(self, page_url: str) -> dict:
        page_content = self.get_page_content(page_url)
        if not page_content:
            return {
                'current_page': None,
                'total_pages': None,
                'next_page_url': None
            }

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
                            if 'p=' in current_url:
                                next_url = current_url.replace(f'p={current_page}', f'p={current_page + 1}')
                            else:
                                next_url = f"{current_url}{'&' if '?' in current_url else '?'}p={current_page + 1}"
                            pagination_info['next_page_url'] = next_url
            return pagination_info
        except Exception as e:
            print(f"Error extracting pagination details: {e}")
            return pagination_info

    def get_product_listings(self, listings_page_url: str, page: int = 1) -> list[str]:
        if page > 1:
            url = f"{listings_page_url}{'&' if '?' in listings_page_url else '?'}p={page}"
        else:
            url = listings_page_url

        page_content = self.get_page_content(url)
        if not page_content:
            print(f"Failed to retrieve content for page {page}")
            return []

        return self._extract_product_listings(page_content, page)

    def _extract_product_listings(self, page_content: str, page: int) -> list[str]:
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            product_links = []
            product_items = soup.find_all('li', class_='product-base')
            
            for item in product_items:
                a_tag = item.find('a', href=True)
                if a_tag:
                    href = a_tag['href']
                    full_url = href if href.startswith('http') else f'https://www.myntra.com/{href.lstrip("/")}'
                    if full_url not in product_links:
                        product_links.append(full_url)
                        
            print(f"Found {len(product_links)} unique product links on page {page}")
            return product_links
        except Exception as e:
            print(f"Error extracting product listings: {e}")
            return []

    def _extract_id(self, soup: BeautifulSoup) -> str | None:
        try:
            id_element = soup.find('span', {'class': 'supplier-styleId'})
            if id_element:
                id_text = id_element.text.strip()
                return f"{self.id_prefix}{id_text}" if id_text else None
            return None
        except Exception as e:
            print(f"Error extracting ID: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        try:
            product_name = soup.find('h1', {'class': 'pdp-name'})
            if product_name:
                title = product_name.text.strip()
                return title if title else None
            return None
        except Exception as e:
            print(f"Error extracting title: {e}")
            return None

    def _extract_price(self, soup: BeautifulSoup) -> int | None:
        try:
            price = soup.find('span', {'class': 'pdp-price'})
            if price:
                price_text = price.text.strip().replace('₹', '').replace(',', '')
                price_value = int(float(price_text))
                return price_value if price_value > 0 else None
            return None
        except (ValueError, AttributeError) as e:
            print(f"Error extracting price: {e}")
            return None

    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        try:
            rating_container = soup.find('div', {'class': 'index-overallRating'})
            if rating_container:
                rating_div = rating_container.find('div')
                if rating_div:
                    rating_text = rating_div.text.strip()
                    rating_value = float(rating_text)
                    return rating_value if 0 <= rating_value <= 5 else None
            return None
        except (ValueError, AttributeError) as e:
            print(f"Error extracting rating: {e}")
            return None

    def _extract_review_count(self, soup: BeautifulSoup) -> int | None:
        try:
            rating_container = soup.find('div', {'class': 'index-overallRating'})
            if rating_container:
                ratings_count = rating_container.find('div', {'class': 'index-ratingsCount'})
                if ratings_count:
                    review_text = ratings_count.text.strip().split()[0]
                    review_count = int(review_text)
                    return review_count if review_count >= 0 else None
            return None
        except (ValueError, AttributeError) as e:
            print(f"Error extracting review count: {e}")
            return None

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        try:
            descriptions_container = soup.find('div', class_='pdp-productDescriptorsContainer')
            if not descriptions_container:
                print("Description container not found.")
                return None
            description_p = descriptions_container.find('p', class_='pdp-product-description-content')
            if not description_p:
                print("Description paragraph not found.")
                return None
            list_items = description_p.find_all('li')
            if list_items:
                description = '\n'.join(item.get_text(strip=True) for item in list_items)
            else:
                description = description_p.get_text(strip=True)

            return description

        except Exception as e:
            print(f"Error extracting description: {e}")
            return None

    def _extract_material(self, soup: BeautifulSoup) -> str | None:
        try:
            # Find all index rows
            index_rows = soup.find_all('div', {'class': 'index-row'})
            for row in index_rows:
                key_div = row.find('div', {'class': 'index-rowKey'})
                if key_div and 'Fabrics' in key_div.text:
                    value_div = row.find('div', {'class': 'index-rowValue'})
                    if value_div:
                        material = value_div.text.strip()
                        return material if material else None
            return None
        except Exception as e:
            print(f"Error extracting material: {e}")
            return None

    def _extract_sizes(self, soup: BeautifulSoup) -> list[str]:
        try:
            sizes = []
            size_buttons = soup.find_all('button', class_='size-buttons-size-button')
            for button in size_buttons:
                size_tag = button.find('p', class_='size-buttons-unified-size')
                if size_tag:
                    size = size_tag.contents[1].strip()
                    sizes.append(size)
            return sizes
        except Exception as e:
            print(f"Error extracting sizes: {e}")
            return []
        
    def _extract_category(self, soup: BeautifulSoup) -> str | None:
        try:
            breadcrumb_container = soup.find('div', class_='breadcrumbs-container')
            if not breadcrumb_container:
                print("Breadcrumb container not found.")
                return None

            links = breadcrumb_container.find_all('a', class_='breadcrumbs-link')

            if len(links) >= 4:
                return links[3].get_text(strip=True)
            else:
                print("Not enough breadcrumb links to extract category.")
                return None

        except Exception as e:
            print(f"Error extracting category: {e}")
            return None

    def _extract_colors(self, soup: BeautifulSoup) -> list[str]:
        try:
            colors = []
            colors_container = soup.find('div',class_= 'colors-container')
            if colors_container:
                color_links = colors_container.find_all('a')
                for link in color_links:
                    color = link.get('title')
                    if color:
                        colors.append(color)
            return colors
        except Exception as e:
            print(f"Error extracting colors: {e}")
            return []

    def _extract_image_url(self, soup: BeautifulSoup) -> str | None:
        try:
            image_container = soup.find('div', {'class': 'image-grid-imageContainer'})
            if image_container:
                image_div = image_container.find('div', {'class': 'image-grid-image'})
                if image_div and 'style' in image_div.attrs:
                    style = image_div['style']
                    url_start = style.find('url("') + 5
                    url_end = style.find('")', url_start)
                    if url_start > 4 and url_end > url_start:
                        image_url = style[url_start:url_end]
                        return image_url if image_url else None
            return None
        except Exception as e:
            print(f"Error extracting image URL: {e}")
            return None

    def get_product_details(self, product_page_url: str) -> Product | dict:
        try:
            page_content = self.get_page_content(product_page_url)
            if not page_content:
                print(f"Failed to retrieve content for product page: {product_page_url}")
                return {}

            soup = BeautifulSoup(page_content, 'html.parser')

            product_data = {
                'id': self._extract_id(soup),
                'title': self._extract_title(soup),
                'price': self._extract_price(soup),
                'rating': self._extract_rating(soup),
                'review_count': self._extract_review_count(soup),
                'description': self._extract_description(soup),
                'category': self._extract_category(soup),
                'material': self._extract_material(soup),
                'sizes': self._extract_sizes(soup),
                'colors': self._extract_colors(soup),
                'image_url': self._extract_image_url(soup),
                'url': product_page_url,
                'processed': False,
                'scraped_datetime': datetime.now(timezone.utc).timestamp(),
                'processed_datetime': datetime.now(timezone.utc).timestamp()
            }

            return Product(**product_data)

        except Exception as e:
            print(f"Error fetching product details: {e}")
            return {}

    def close(self):
        if self.content_loader:
            self.content_loader.close()

if __name__ == "__main__":
    # Initialize scraper with headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    print("Initializing Myntra Scraper...")
    scraper = MyntraScraper(headers=headers)

    try:
        # Test search URL
        search_url = "https://www.myntra.com/cargos"
        print(f"\nTesting search URL: {search_url}")

        # Test page content retrieval
        print("\n1. Testing page content retrieval...")
        html_content = scraper.get_page_content(search_url)
        if html_content:
            print(f"✓ Successfully retrieved {len(html_content)} characters of HTML")
        else:
            print("✗ Failed to retrieve content")
            exit(1)

        # Test pagination details
        print("\n2. Testing pagination details...")
        pagination_details = scraper.get_pagination_details(search_url)
        print("Pagination Details:")
        for key, value in pagination_details.items():
            print(f"  {key}: {value}")

        # Test product listings
        print("\n3. Testing product listings...")
        product_links = scraper.get_product_listings(search_url)
        print(f"Found {len(product_links)} products on first page")
        
        if product_links:
            print("\nSample Product Links:")
            for i, link in enumerate(product_links[:3], 1):
                print(f"  {i}. {link}")

            # Test product details
            print("\n4. Testing product details extraction...")
            test_product_url = product_links[0]
            print(f"Testing with product: {test_product_url}")
            
            product_details = scraper.get_product_details(test_product_url)
            if product_details:
                print("\nProduct Details:")
                for key, value in product_details.__dict__.items():
                    if not key.startswith('_'):
                        print(f"  {key}: {value}")
            else:
                print("✗ Failed to extract product details")

    except Exception as e:
        print(f"\nError during testing: {e}")
    finally:
        print("\nCleaning up resources...")
        scraper.close()
        print("Done!")
