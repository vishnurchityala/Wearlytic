from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraperkit.base import BaseScraper
from scraperkit.loaders import SeleniumContentLoader
from scraperkit.exceptions import ContentNotLoadedException, DataComponentNotFoundException, DataParsingException
from scraperkit.models import Product

class JayWalkingScraper(BaseScraper):
    """
    JayWalkingScraper extracts structured product data from Jaywalking.in by parsing listing and product pages.
    It extends BaseScraper and returns results as Product objects.
    """

    def __init__(self, base_url=None, headers = None, content_loader=None):
        super().__init__("https://www.jaywalking.in/", headers=headers or {})
        self.id_prefix = "jywlkng_"
        self.content_loader = content_loader or SeleniumContentLoader()     

    def get_page_content(self, page_url):
        try:
            return self.content_loader.load_content(page_url=page_url)
        except Exception:
            raise ContentNotLoadedException(f"Failed to Load Page Content of Page URL : {page_url}")

    def get_pagination_details(self, page_url):
        
        page_content = self.get_page_content(page_url=page_url)
        
        soup = BeautifulSoup(page_content,"html.parser")
        
        pagination_div = soup.find("div",attrs={"class":"pagination pagination--"})
        
        if pagination_div == None:
            return {
                'current_page': page_url,
                'total_pages': 1,
                'next_page_url': None
            }
        
        try:
            next_page_url = self.base_url[:-1]+ pagination_div.find("a",attrs={"class":"next"})['href'].split('&')[0]
            total_pages = int(pagination_div.find_all("a",attrs={"class":"page"})[-1].text)

            return {
                    'current_page': page_url,
                    'total_pages': total_pages,
                    'next_page_url' : next_page_url
                }
        except Exception:
            raise DataParsingException("Failed to Parse Data for Pagination Details in JayWalking.")
    
    def get_product_listings(self, listings_page_url, page = 1):
        page_content = self.get_page_content(listings_page_url)
        soup = BeautifulSoup(page_content,"html.parser")
        try:
            product_links = []
            product_link_eles = soup.find_all("a",attrs={"class":"product-item__special-link"})
            for product_link in product_link_eles:
                if ("gift-card" not in product_link["href"]):
                    product_links.append(self.base_url[:-1]+product_link["href"])
            return product_links
        except Exception:
            raise DataParsingException("Failed to Parse Data for Product Listings in JayWalking.")

    def _extract_title(self, soup: BeautifulSoup) -> str:
        try:
            return soup.find("h1",attrs={"class":"product-title"}).text
        except Exception:
            raise DataParsingException("Failed to Parse Data for Product Title in JayWalking.")

    def _extract_id(self, soup: BeautifulSoup) -> str:
        try:
            title = self._extract_title(soup)
            id = self.id_prefix + "_".join(title.lower().split()[:-1])
            return id
        
        except Exception:
            raise DataParsingException("Failed to Parse Data for Product ID in JayWalking.")

    def _extract_category(self, soup: BeautifulSoup) -> str:
        return "Dummy String"

    def _extract_price(self, soup: BeautifulSoup) -> float:
        try:
            price = soup.find("span",attrs={"class":"product-price"})
            if price == None:
                raise DataComponentNotFoundException("Failed to find Data Component for Price in JayWalking.")
            price = float(price.text.split()[-1].replace(',',''))
            return price
        except DataComponentNotFoundException as e:
            raise e
        except Exception:
            raise DataParsingException("Failed to Parse Data for Price in JayWalking.")

    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        try:
            sizes_labels = soup.find_all("label",attrs={"class":"product-variant__label"})
            if sizes_labels == None:
                raise DataComponentNotFoundException("Failed to Find Data Component for Sizes in JayWalking.")
            sizes = []
            for size_label in sizes_labels:
                sizes.append(size_label.text)
            return sizes
        except DataComponentNotFoundException as e:
            raise e
        except Exception:
            raise DataParsingException("Failed to Parse Data for Sizes in JayWalking.")

    def _extract_description(self, soup: BeautifulSoup) -> str:
        try:
            description_container = soup.find("div", class_="rte")
            if not description_container:
                raise DataComponentNotFoundException("Failed to Find Data Component for Description in JayWalking.")
            
            size_chart_table = description_container.find("table")
            if size_chart_table:
                size_chart_table.decompose()
            
            size_chart_heading = description_container.find(string=lambda text: text and "SIZE CHART" in text.upper())
            if size_chart_heading:
                size_chart_heading.parent.decompose()
            
            description_text = description_container.get_text(separator=" ", strip=True)
            
            return description_text.lower().capitalize()
        
        except DataComponentNotFoundException as e:
            raise e
        except Exception:
            raise DataParsingException("Failed to Parse Data for Description in JayWalking.")

    def _extract_material(self, soup: BeautifulSoup) -> str:
        try:
            description = self._extract_description(soup).lower()

            possible_keywords = [
                "composition & care",
                "composition and care",
            ]

            idx = -1
            for keyword in possible_keywords:
                idx = description.find(keyword)
                if idx != -1:
                    break

            if idx == -1:
                raise DataComponentNotFoundException(
                    "Failed to Find Data Component for Material in JayWalking."
                )

            after_comp = description[idx + len(keyword):].lstrip(" :.&")

            splitters = [".", ",", "note", "features", "size", "wash", "\n"]
            next_stop = len(after_comp)

            for splitter in splitters:
                split_idx = after_comp.find(splitter)
                if split_idx != -1:
                    next_stop = min(next_stop, split_idx)

            material = " ".join(after_comp[:next_stop].strip().split()[:-1])

            if not material:
                raise DataComponentNotFoundException(
                    "Found composition keyword but no material text following it."
                )

            return material

        except DataComponentNotFoundException as e:
            raise e
        except Exception:
            raise DataParsingException(
                "Failed to Parse Data for Material in JayWalking."
            )

    def _extract_image_url(self, soup: BeautifulSoup) -> list:
        try:
            img = soup.find_all("div",attrs={"class":"product-gallery-item"})[0].find("img")
            if img == None:
                raise DataComponentNotFoundException("Failed to Find Data Component for Image in JayWalking.")
            return "https:"+img["src"]
        except DataComponentNotFoundException as e:
            raise e
        except Exception:
            raise DataParsingException("Failed to Parse Data for Image in JayWalking.")

    def _extract_gender(self, soup: BeautifulSoup) -> str:
        try:
            title = self._extract_title(soup).lower()
            if 'unisex' in title:
                return "Unisex"
            else:
                return "Woman"
        except DataComponentNotFoundException as e:
            raise e
        except Exception:
            raise DataParsingException("Failed to Parse Data for Gender in JayWalking.")

    def _extract_colors(self, soup: BeautifulSoup) -> list:
        return []

    def _extract_rating(self, soup: BeautifulSoup) -> float:
        return 0.0

    def _extract_review_count(self, soup: BeautifulSoup) -> int:    
        return 0

    def get_product_details(self, product_page_url):
        try:
            page_content = self.get_page_content(product_page_url)
            soup = BeautifulSoup(page_content,"html.parser")
            category = product_page_url.split("/collections/")[1].split("/")[0].capitalize()  
            product = Product(
                id=self._extract_id(soup),
                title=self._extract_title(soup),
                price=self._extract_price(soup),
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
                page_content=page_content
            )
            return product
        except Exception as e:
            if isinstance(e, (DataComponentNotFoundException, DataParsingException, ContentNotLoadedException)):
                raise
            raise DataParsingException(f"Error extracting product details from {product_page_url}: {str(e)}")

    def close(self):
        if self.content_loader:
            self.content_loader.close()