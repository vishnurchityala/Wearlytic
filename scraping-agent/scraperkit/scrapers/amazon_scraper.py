from bs4 import BeautifulSoup
from scraperkit.base import BaseScraper
from scraperkit.loaders import SeleniumContentLoader
from scraperkit.models import Product
from scraperkit.exceptions import DataComponentNotFoundException, DataParsingException
from datetime import datetime,timezone

class AmazonScraper(BaseScraper):
    """
    AmazonScraper extracts structured product data from Amazon India by parsing listing and product pages.
    It extends BaseScraper and returns results as Product objects.
    """
    def __init__(self, headers=None,content_loader=None):
        super().__init__("https://www.amazon.in/", headers=headers)
        self.id_prefix = "amzn_"
        self.content_loader = content_loader or SeleniumContentLoader(headers=headers)

    def get_page_content(self, page_url: str) -> str | None:
        return self.content_loader.load_content(page_url)

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
            raise e
        
    def get_product_listings(self, listings_page_url: str, page: int = 1) -> list[str]:
        if page > 1:
            url = f"{listings_page_url}&page={page}" if '?' in listings_page_url else f"{listings_page_url}?page={page}"
        else:
            url = listings_page_url

        page_content = self.get_page_content(url)
        if not page_content:
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
                raise DataComponentNotFoundException("detailBullets_feature_div not found")

            try:
                items = details_div.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if 'ASIN' in text:
                        asin = text.split(':')[-1].strip()
                        if asin:
                            return f"{self.id_prefix}{asin}"
                        else:
                            raise DataParsingException("ASIN value empty")
                
                raise DataComponentNotFoundException("ASIN not found in detailBullets_feature_div")

            except Exception as inner_exception:
                raise DataParsingException(f"Error parsing ASIN from detailBullets_feature_div: {inner_exception}") from inner_exception

        except Exception as e:
            raise e

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        try:
            details_div = soup.find("span", id="productTitle")
            if not details_div:
                raise DataComponentNotFoundException("productTitle span not found")

            title = details_div.get_text(strip=True)
            if not title:
                raise DataParsingException("productTitle text is empty")

            return title

        except Exception as e:
            raise e

    def _extract_price(self, soup: BeautifulSoup) -> int | None:
        try:
            price_element = soup.find("span", class_="a-price-whole")
            if not price_element:
                raise DataComponentNotFoundException("Price element with class 'a-price-whole' not found")

            price_text = price_element.text.strip()
            if not price_text:
                raise DataParsingException("Price text is empty")

            try:
                price = int(price_text.replace(",", ""))
            except ValueError:
                raise DataParsingException(f"Price text '{price_text}' is not a valid integer")

            if price <= 0:
                raise DataParsingException(f"Price value {price} is not positive")

            return price

        except Exception as e:
            raise e

    def _extract_category(self, soup: BeautifulSoup) -> str | None:
        try:
            breadcrumb_div = soup.find("div", id="wayfinding-breadcrumbs_feature_div")
            if not breadcrumb_div:
                raise DataComponentNotFoundException("Breadcrumb div with id 'wayfinding-breadcrumbs_feature_div' not found")

            breadcrumb_links = breadcrumb_div.find_all("a", class_="a-link-normal a-color-tertiary")
            if not breadcrumb_links:
                raise DataComponentNotFoundException("No breadcrumb links with class 'a-link-normal a-color-tertiary' found")

            category = breadcrumb_links[-1].get_text(strip=True)
            if not category:
                raise DataParsingException("Category text is empty")

            return category

        except Exception as e:
            raise e

    def _extract_gender(self, soup: BeautifulSoup) -> str | None:
        try:
            detail_div = soup.find("div", id="detailBullets_feature_div")
            if not detail_div:
                raise DataComponentNotFoundException("detailBullets_feature_div not found")
            
            for li in detail_div.find_all("li"):
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
            raise DataParsingException(f"Error extracting gender: {e}")

    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        try:
            img_wrapper = soup.find("div", id="imgTagWrapperId")
            if not img_wrapper:
                raise DataComponentNotFoundException("Image wrapper div with id 'imgTagWrapperId' not found")
            
            img_tag = img_wrapper.find("img")
            if not img_tag:
                raise DataComponentNotFoundException("Image tag inside 'imgTagWrapperId' div not found")
            
            image_url = img_tag.get("src")
            if not image_url:
                raise DataParsingException("Image URL (src attribute) is missing or empty")
            
            return image_url

        except Exception as e:
            raise e

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
            if not size_spans:
                raise DataParsingException("Size spans not found within size container")
            
            for span in size_spans:
                size_text = span.get_text(strip=True)
                if size_text:
                    sizes.append(size_text)
                else:
                    raise DataParsingException("Empty size text found in size span")
            
            return sizes
        
        except Exception as e:
            raise e

    def _extract_material(self, soup: BeautifulSoup) -> str | None:
        try:
            product_facts = soup.find_all('div', class_='a-fixed-left-grid product-facts-detail')
            path = "a-fixed-left-grid product-facts-detail"
            if not product_facts:
                raise DataComponentNotFoundException(f"Material infor container was not found {path}")
            
            for fact in product_facts:
                label_div = fact.find('div', class_='a-col-left')
                if not label_div:
                    continue
                    
                label = label_div.get_text(strip=True).lower()
                if label in ('material', 'material type', 'material composition'):
                    value_div = fact.find('div', class_='a-col-right')
                    if not value_div:
                        raise DataParsingException("Material value div not found")
                    
                    material = value_div.get_text(strip=True)
                    if material:
                        return material
                    else:
                        raise DataParsingException("Material text is empty")
            
            raise DataParsingException("Material value was not parsed.")

        except Exception as e:
            raise e

    def _extract_description(self, soup: BeautifulSoup) -> str:
        try:
            description_div = soup.find("div", id="productFactsDesktopExpander")
            if not description_div:
                raise DataComponentNotFoundException("Description container not found")

            additional_info_div = description_div.find("ul", class_="a-unordered-list a-vertical a-spacing-small")
            if not additional_info_div:
                raise DataComponentNotFoundException("Description list not found inside description container")

            description = additional_info_div.get_text(strip=True)
            if not description:
                raise DataParsingException("Description text is empty")

            return description

        except Exception as e:
            raise e

    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        try:
            rating_element = soup.find("span", id="acrPopover")
            if not rating_element:
                return None
            
            if 'title' not in rating_element.attrs:
                raise DataParsingException("Rating attribute 'title' not found")
            
            rating_text = rating_element.get('title').split()[0]
            
            try:
                rating = float(rating_text)
            except ValueError:
                raise DataParsingException(f"Rating value is not a float: {rating_text}")
            
            if not (0 <= rating <= 5):
                raise DataParsingException(f"Rating value {rating} out of valid range (0-5)")
            
            return rating
        
        except Exception as e:
            raise e

    def _extract_review_count(self, soup: BeautifulSoup) -> int | None:
        try:
            review_element = soup.find("span", id="acrCustomerReviewText")
            if not review_element:
                return None
            
            if 'aria-label' not in review_element.attrs:
                raise DataParsingException("Review count attribute 'aria-label' not found")
            
            review_text = review_element.get('aria-label').split()[0].replace(",", "")
            
            try:
                review_count = int(float(review_text))
            except ValueError:
                raise DataParsingException(f"Review count is not a valid number: {review_text}")
            
            if review_count < 0:
                raise DataParsingException(f"Review count {review_count} cannot be negative")
            
            return review_count
        
        except Exception as e:
            raise e

    def get_product_details(self, product_page_url: str) -> Product | dict:
        try:
            if '?' in product_page_url:
                product_page_url = product_page_url.split('?')[0]
                
            page_content = self.get_page_content(product_page_url)

            soup = BeautifulSoup(page_content, 'html.parser')
            body_content = soup.body.prettify()
            
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
                processed_datetime=datetime.now(timezone.utc).timestamp(),
                page_content=body_content
            )

        except Exception as e:
            print(f"Error fetching product details: {e}")
            return {}

    def close(self):
        if self.content_loader:
            self.content_loader.close()