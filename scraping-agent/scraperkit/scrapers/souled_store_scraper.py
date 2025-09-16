import bs4
from bs4 import BeautifulSoup
from scraperkit.base import BaseScraper
from scraperkit.loaders import SeleniumInfinityScrollContentLoader, SeleniumContentLoader
from scraperkit.models.product import Product
from scraperkit.exceptions import (
    DataComponentNotFoundException,
    DataParsingException,
    ContentNotLoadedException
)
from datetime import datetime, timezone

class SouledStoreScraper(BaseScraper):
    """
    SouledStoreScraper extracts structured product data from The Souled Store by parsing listing and product pages.
    It extends BaseScraper and returns results as Product objects.
    """    
    def __init__(self,headers=None,content_loader=None):
        super().__init__("https://www.thesouledstore.com/", headers=headers or {})
        self.id_prefix = "sstore_"
        self.content_loader = content_loader or SeleniumInfinityScrollContentLoader(
            max_scrolls= 30,
            target_class_name= "tss-footer",
            scroll_delay=10,
            headless=True            
        )
        
    def get_page_content(self, page_url):
        try:
            content = self.content_loader.load_content(page_url=page_url)
            if not content:
                raise ContentNotLoadedException(f"Failed to load content from {page_url}")
            return content
        except Exception as e:
            if isinstance(e, ContentNotLoadedException):
                raise
            raise ContentNotLoadedException(f"Error loading content from {page_url}: {str(e)}")
    
    def get_pagination_details(self, page_url):
        return {
                'current_page': page_url,
                'total_pages': 1,
                'next_page_url': None
            }
    
    def get_product_listings(self, listings_page_url, page = 1):
        try:
            page_content = self.get_page_content(listings_page_url)
            soup = BeautifulSoup(page_content,"html.parser")
            product_links = []
            product_cards = soup.find_all('div',class_="productCard")
            
            if not product_cards:
                raise DataComponentNotFoundException("No product cards found on the page")
                
            for product_card in product_cards:
                product_link_tag = product_card.find('a')
                if product_link_tag and 'href' in product_link_tag.attrs:
                    product_link = product_link_tag['href']
                    if product_link.startswith('/'):
                        product_link = self.base_url[:-1] + product_link
                    product_links.append(product_link)
            
            if not product_links:
                raise DataComponentNotFoundException("No product links found in product cards")
                
            return product_links
        except Exception as e:
            if isinstance(e, (DataComponentNotFoundException, ContentNotLoadedException)):
                raise
            raise DataParsingException(f"Error parsing product listings from {listings_page_url}: {str(e)}")

    def _extract_id(self, soup: BeautifulSoup, title: str) -> str:
        return f"{self.id_prefix}{title.replace(' ', '_').lower()}"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('h1', class_='fbold mb-0 title-size')
        if not title_tag:
            raise DataComponentNotFoundException("Product title not found")
        return title_tag.get_text(strip=True)

    def _extract_category(self, soup: BeautifulSoup) -> str:
        cat_tag = soup.find('h1', class_='prod-cat')
        if not cat_tag:
            raise DataComponentNotFoundException("Product category not found")
        return cat_tag.get_text(strip=True)

    def _extract_price(self, soup: BeautifulSoup) -> float:
        price_tag = soup.find('span', class_='leftPrice pull-right')
        if price_tag:
            price_inner = price_tag.find('span', class_='fbold')
            if price_inner:
                price_text = price_inner.get_text(strip=True).replace('₹', '').replace(',', '')
                try:
                    return float(price_text)
                except ValueError:
                    raise DataParsingException(f"Failed to parse price: {price_text}")

        offer_tag = soup.find('span', class_='offer')
        if offer_tag:
            price_text = offer_tag.get_text(strip=True).replace('₹', '').replace(',', '')
            try:
                return float(price_text)
            except ValueError:
                raise DataParsingException(f"Failed to parse offer price: {price_text}")

        raise DataComponentNotFoundException("Product price not found")

    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        sizes = []
        sizelist = soup.find('ul', class_='sizelist')
        if sizelist and hasattr(sizelist, 'find_all'):
            for li in sizelist.find_all('li'):
                span = li.find('span', class_='sizetext')
                if span:
                    sizes.append(span.get_text(strip=True))
                else:
                    label = li.find('label')
                    if label:
                        sizes.append(label.get_text(strip=True))
        return sizes

    def _extract_description(self, soup: BeautifulSoup) -> str:
        desc_div = soup.find('div', id='collapseTwo')
        if desc_div:
            card_block = desc_div.find('div', class_='card-block')
            if card_block:
                return card_block.get_text(strip=True)
        raise DataComponentNotFoundException("No product description card found on the page")

    def _extract_material(self, soup: BeautifulSoup) -> str:
        for card_block in soup.find_all('div', class_='card-block'):
            text = card_block.get_text(' ', strip=True)
            if 'Material & Care' in text:
                lines = text.split('Material & Care:')
                if len(lines) > 1:
                    return lines[1].split('Country of Origin')[0].strip().replace('\n', ' ')
        raise DataComponentNotFoundException("No material cards found on the page")

    def _extract_image_url(self, soup: BeautifulSoup) -> list:
        urls = []
        try:
            img_divs = soup.find_all('div', class_='pimg')
        except Exception:
            raise DataComponentNotFoundException("Product Image Component Not Found.")
        for div in img_divs:
            img = div.find('img')
            if img:
                # Prefer src, fallback to data-src or data-url if available
                src = img.get('src') or img.get('data-src') or img.get('data-url')
                if src:
                    urls.append(src)
        return urls[0]

    def _extract_gender(self, soup: BeautifulSoup) -> str:
        active_cat = soup.find('li', class_='activeCat')
        if active_cat:
            a_tag = active_cat.find('a')
            if a_tag and a_tag.get_text(strip=True):
                text = a_tag.get_text(strip=True).lower()
                if 'men' in text:
                    return 'Men'
                elif 'women' in text:
                    return 'Women'
                elif 'sneakers' in text:
                    return 'Sneakers'
                else:
                    return a_tag.get_text(strip=True).title()
        raise DataComponentNotFoundException("No gender component found on the page")

    def _extract_colors(self, soup: BeautifulSoup) -> list:
        return []

    def _extract_rating(self, soup: BeautifulSoup) -> float:
        return 0.0

    def _extract_review_count(self, soup: BeautifulSoup) -> int:
        return 0

    def get_product_details(self, product_page_url):
        try:
            loader = SeleniumContentLoader()
            page_content = loader.load_content(page_url=product_page_url)
            soup = BeautifulSoup(page_content, "html.parser")
            body_content = soup.body.prettify()
            
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            category = self._extract_category(soup)
            gender = product_page_url
            if "men" in product_page_url:
                gender = "men"
            elif "women" in product_page_url:
                gender = "women"
            else:
                gender = "N/A"
            
            product = Product(
                id=self._extract_id(soup, title),
                title=title,
                price=price,
                category=category,
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
                scraped_datetime=datetime.now(timezone.utc),
                processed_datetime=datetime.now(timezone.utc),
                page_index=0,
                page_content=body_content
            )
            return product
        except Exception as e:
            if isinstance(e, (DataComponentNotFoundException, DataParsingException, ContentNotLoadedException)):
                raise
            raise DataParsingException(f"Error extracting product details from {product_page_url}: {str(e)}")

    def close(self):
        if self.content_loader:
            self.content_loader.close()