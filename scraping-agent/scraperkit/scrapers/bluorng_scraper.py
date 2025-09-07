from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraperkit.base import BaseScraper
from scraperkit.loaders import SeleniumInfinityScrollContentLoader
from scraperkit.exceptions import ContentNotLoadedException, DataComponentNotFoundException, DataParsingException
from scraperkit.models import Product

class BluOrngScraper(BaseScraper):
    """
    BluOrngScraper extracts structured product data from bluorng.com by parsing listing and product pages.
    It extends BaseScraper and returns results as Product objects.
    """
    
    def __init__(self,headers=None,content_loader=None):
        super().__init__("https://bluorng.com/", headers=headers or {})
        self.id_prefix = "bluorng_"
        self.content_loader = content_loader or SeleniumInfinityScrollContentLoader(
            max_scrolls= 30,
            target_class_name= "f-marquee",
            scroll_delay=6,
            headless=True           
        )
    
    def get_page_content(self, page_url):
        try:
            content = self.content_loader.load_content(page_url=page_url)
            return content
        except Exception:
            raise ContentNotLoadedException(f"Error while loading page content of page url: {page_url}")
    
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
            product_cards = soup.find_all("div",attrs={"class":"card__content"})

            if not product_cards:
                raise DataComponentNotFoundException(f"Product Component Not Found in Listings Page : {listings_page_url}")
            try:
                for product_card in product_cards:
                    product_link = product_card.find("a")['href']
                    product_link = self.base_url + product_link[1:]
                    product_links.append(product_link)
            except Exception as e:
                raise DataParsingException(f"Error parsing product card from {listings_page_url}")
            
            return product_links
        
        except Exception as e:
            if isinstance(e, (DataComponentNotFoundException, ContentNotLoadedException)):
                            raise
            raise DataParsingException(f"Error parsing product listings from {listings_page_url}: {str(e)}")
    
    def _extract_id(self, soup: BeautifulSoup) -> str:
        try:
            id = soup.find("div",attrs={"class":"product__title"})
            id = id.find("h1")
            id = id.text
            id_str = self.id_prefix[:-1]
            for word in id.split():
                id_str += "_" + word.lower().replace("-","_")
            return id_str
        except Exception:
            raise DataComponentNotFoundException("Id Data Component Not Found for BluOrgn")

    def _extract_title(self, soup: BeautifulSoup) -> str:
        try:
            title = soup.find("div",attrs={"class":"product__title"})
            title = title.find("h1")
            title = title.text
            return title.capitalize()
        except Exception:
            raise DataComponentNotFoundException("Title Data Component Not Found for BluOrgn")

    def _extract_category(self, soup: BeautifulSoup) -> str:
        try:
            category = soup.find("div",attrs={"class":"product__title"})
            category = category.find("h1")
            category = category.text.split()[-1]
            return category.capitalize()
        except Exception:
            raise DataComponentNotFoundException("Category Data Component Not Found for BluOrgn")

    def _extract_price(self, soup: BeautifulSoup) -> float:
        try:
            price = float(soup.find("span",attrs={"class":"price-item price-item--sale price-item--last"}).text.split()[-1].replace(",",""))
            return price  
        except Exception:
            raise DataComponentNotFoundException("Price Data Component Not Found for BluOrng")

    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        try:
            sizes_div = soup.find("fieldset",attrs={"class":"js product-form__input"})
            sizes_components = sizes_div.find_all("input",attrs={"name":"Size"})
            sizes = []
            for size_component in sizes_components:
                size = size_component["value"]
                sizes.append(size)
            return sizes
        except Exception:
            raise DataComponentNotFoundException("Sizes Data Component Not Found for BluOrng")

    def _extract_description(self, soup: BeautifulSoup) -> str:
        try:
            return soup.find("div", class_="product-details-desc").get_text(strip=True)
        except Exception:
            raise DataComponentNotFoundException("Description Data Component Not Found in BluOrng")

    def _extract_material(self, soup: BeautifulSoup) -> str:
        return None

    def _extract_image_url(self, soup: BeautifulSoup) -> list:
        try:
            images = soup.find_all("div",attrs={"class":"product__media media media--transparent"})
            image = "https:"+images[0].find("img")["src"]
            return image
        except Exception:
            raise DataComponentNotFoundException("Image Data Component Not Found in BluOrng")

    def _extract_gender(self, soup: BeautifulSoup) -> str:
        return "Unisex"

    def _extract_colors(self, soup: BeautifulSoup) -> list:
        return []

    def _extract_rating(self, soup: BeautifulSoup) -> float:
        return 0.0

    def _extract_review_count(self, soup: BeautifulSoup) -> int:
        return 0

    def get_product_details(self, product_page_url):
        try:
            page_content = self.get_page_content(product_page_url)
            soup = BeautifulSoup(page_content, "html.parser")
            body_content = soup.body.prettify()
            
            product = Product(
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