from bs4 import BeautifulSoup
from scraperkit.base.base_scraper import BaseScraper
from scraperkit.loaders.selenium_content_loader import SeleniumContentLoader
from scraperkit.models.product import Product
from datetime import datetime,timezone

class AmazonScraper(BaseScraper):
    def __init__(self, headers=None,content_loader=None):
        super().__init__("https://www.amazon.in/", headers=headers)
        self.id_prefix = "amzn_"
        self.content_loader = content_loader or SeleniumContentLoader(headers=headers)

    def get_page_content(self, page_url: str) -> str | None:
        try:
            return self.content_loader.load_content(page_url)
        except Exception as e:
            print(f"Error fetching page content: {e}")
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
        except Exception as e:
            print(f"Error extracting pagination details: {e}")
            return pagination_info

    def get_product_listings(self, listings_page_url: str, page: int = 1) -> list[str]:
        if page > 1:
            url = f"{listings_page_url}&page={page}" if '?' in listings_page_url else f"{listings_page_url}?page={page}"
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

    def _extract_id(self, soup: BeautifulSoup) -> str | None:
        try:
            details_div = soup.find("div", id="detailBullets_feature_div")
            if not details_div:
                return None
                
            items = details_div.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if 'ASIN' in text:
                    asin = text.split(':')[-1].strip()
                    return f"{self.id_prefix}{asin}" if asin else None
            return None
        except Exception as e:
            print(f"Error extracting ID: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        try:
            details_div = soup.find("span", id="productTitle")
            if not details_div:
                return None
            title = details_div.get_text(strip=True)
            return title
        except Exception as e:
            print(f"Error extracting title: {e}")
            return None

    def _extract_price(self, soup: BeautifulSoup) -> int | None:
        try:
            price_element = soup.find("span", class_="a-price-whole")
            if not price_element:
                return None
                
            price_text = price_element.text.strip()
            if not price_text:
                return None
                
            price = int(price_text.replace(",", ""))
            return price if price > 0 else None
        except (ValueError, AttributeError) as e:
            print(f"Error extracting price: {e}")
            return None

    def _extract_category(self, soup: BeautifulSoup) -> str | None:
        try:
            breadcrumb_div = soup.find("div", id="wayfinding-breadcrumbs_feature_div")
            if not breadcrumb_div:
                return None
                
            breadcrumb_links = breadcrumb_div.find_all("a", class_="a-link-normal a-color-tertiary")
            if not breadcrumb_links:
                return None
                
            category = breadcrumb_links[-1].get_text(strip=True)
            return category if category else None
        except Exception as e:
            print(f"Error extracting category: {e}")
            return None

    def _extract_gender(self, soup: BeautifulSoup) -> str | None:
        try:
            for li in soup.select("#detailBullets_feature_div li"):
                key_span = li.select_one("span.a-text-bold")
                if not key_span:
                    continue
                    
                if "Department" in key_span.get_text(strip=True):
                    value_span = key_span.find_next_sibling("span")
                    if value_span:
                        gender = value_span.get_text(strip=True)
                        return gender if gender else None
            return None
        except Exception as e:
            print(f"Error extracting gender: {e}")
            return None

    def _extract_image_url(self, soup: BeautifulSoup) -> str | None:
        try:
            img_wrapper = soup.find("div", id="imgTagWrapperId")
            if not img_wrapper:
                return None
                
            img_tag = img_wrapper.find("img")
            if not img_tag:
                return None
                
            image_url = img_tag.get("src")
            return image_url if image_url else None
        except Exception as e:
            print(f"Error extracting image URL: {e}")
            return None

    def _extract_colors(self, soup: BeautifulSoup) -> list[str]:
        try:
            color_images = soup.find_all('img', class_='swatch-image')
            if not color_images:
                return []
                
            colors = set()
            for img in color_images:
                color = img.get('alt')
                if color:
                    colors.add(color)
            return list(colors)
        except Exception as e:
            print(f"Error extracting colors: {e}")
            return []

    def _extract_sizes(self, soup: BeautifulSoup) -> list[str]:
        try:
            sizes = []
            parent_container = soup.find(id="inline-twister-expander-content-size_name")
            if not parent_container:
                return []
                
            size_spans = parent_container.find_all('span', class_='swatch-title-text-display')
            for span in size_spans:
                size_text = span.get_text(strip=True)
                if size_text:
                    sizes.append(size_text)
            return sizes
        except Exception as e:
            print(f"Error extracting sizes: {e}")
            return []

    def _extract_material(self, soup: BeautifulSoup) -> str | None:
        try:
            product_facts = soup.find_all('div', class_='a-fixed-left-grid product-facts-detail')
            for fact in product_facts:
                label_div = fact.find('div', class_='a-col-left')
                if not label_div:
                    continue
                    
                label = label_div.get_text(strip=True).lower()
                if label == 'material' or label == 'material type' or label == 'material composition':
                    value_div = fact.find('div', class_='a-col-right')
                    if value_div:
                        material = value_div.get_text(strip=True)
                        return material if material else None
            return None
        except Exception as e:
            print(f"Error extracting material: {e}")
            return None

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        try:
            description_div = soup.find("div", id="productFactsDesktopExpander")
            additional_info_div = description_div.find("ul",class_="a-unordered-list a-vertical a-spacing-small")
            if not additional_info_div:
                return None
                
            description = additional_info_div.get_text(strip=True)
            return description if description else None
        except Exception as e:
            print(f"Error extracting description: {e}")
            return None

    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        try:
            rating_element = soup.find("span", id="acrPopover")
            if not rating_element or 'title' not in rating_element.attrs:
                return None
                
            rating_text = rating_element.get('title').split()[0]
            rating = float(rating_text)
            return rating if 0 <= rating <= 5 else None
        except (ValueError, AttributeError) as e:
            print(f"Error extracting rating: {e}")
            return None

    def _extract_review_count(self, soup: BeautifulSoup) -> int | None:
        try:
            review_element = soup.find("span", id="acrCustomerReviewText")
            if not review_element or 'aria-label' not in review_element.attrs:
                return None
                
            review_text = review_element.get('aria-label').split()[0].replace(",", "")
            review_count = int(float(review_text))
            return review_count if review_count >= 0 else None
        except (ValueError, AttributeError) as e:
            print(f"Error extracting review count: {e}")
            return None

    def get_product_details(self, product_page_url: str) -> Product | dict:
        try:
            if '?' in product_page_url:
                product_page_url = product_page_url.split('?')[0]
                
            page_content = self.get_page_content(product_page_url)
            if not page_content:
                print(f"Failed to retrieve content for product page: {product_page_url}")
                return {}

            soup = BeautifulSoup(page_content, 'html.parser')
            
            return Product(
                id=self._extract_id(soup),
                title=self._extract_title(soup),
                price=self._extract_price(soup),
                category=self._extract_category(soup),
                gender=self._extract_gender(soup),
                url=product_page_url,
                image_url=self._extract_image_url(soup),
                colors=self._extract_colors(soup),
                sizes=self._extract_sizes(soup),
                material=self._extract_material(soup),
                description=self._extract_description(soup),
                rating=self._extract_rating(soup),
                review_count=self._extract_review_count(soup),
                processed=False,
                scraped_datetime=datetime.now(timezone.utc).timestamp(),
                processed_datetime=datetime.now(timezone.utc).timestamp()
            )

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
    
    print("Initializing Amazon Scraper...")
    scraper = AmazonScraper(headers=headers)

    try:
        # Test search URL
        search_url = "https://www.amazon.in/s?k=cargos"
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
            for i, link in enumerate(product_links[:10], 1):
                print(f"  {i}. {link}")

            # Test product details
            print("\n4. Testing product details extraction...")
            for test_product_url in product_links[:10]:
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
