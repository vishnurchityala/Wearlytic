from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraperkit.base import BaseScraper
from scraperkit.loaders import SeleniumContentLoader
from scraperkit.exceptions import (
    ContentNotLoadedException,
    DataComponentNotFoundException,
    DataParsingException,
)
from scraperkit.models import Product


class JayWalkingScraper(BaseScraper):
    """
    JayWalkingScraper extracts structured product data from Jaywalking.in by parsing listing and product pages.
    It extends BaseScraper and returns results as Product objects.
    """

    def __init__(self, base_url=None, headers=None, content_loader=None):
        super().__init__("https://www.jaywalking.in/", headers=headers or {})
        self.id_prefix = "jywlkng_"
        self.content_loader = content_loader or SeleniumContentLoader()

    def get_page_content(self, page_url):
        try:
            return self.content_loader.load_content(page_url=page_url)
        except Exception as e:
            if isinstance(e, ContentNotLoadedException):
                raise
            raise ContentNotLoadedException(
                f"Failed to load page content for page URL: {page_url}: {str(e)}"
            ) from e

    def get_pagination_details(self, page_url):
        try:
            page_content = self.get_page_content(page_url=page_url)
            soup = BeautifulSoup(page_content, "html.parser")
            pagination_div = soup.find("div", attrs={"class": "pagination pagination--"})

            if pagination_div is None:
                return {
                    'current_page': page_url,
                    'total_pages': 1,
                    'next_page_url': None
                }

            next_tag = pagination_div.find("a", attrs={"class": "next"})
            if next_tag and next_tag.get("href"):
                next_page_url = self.base_url.rstrip("/") + next_tag["href"].split("&")[0]
            else:
                next_page_url = None

            page_links = pagination_div.find_all("a", attrs={"class": "page"})
            if not page_links:
                raise DataComponentNotFoundException(
                    "Failed to find pagination page links in JayWalking."
                )

            total_pages = int(page_links[-1].text)

            return {
                'current_page': page_url,
                'total_pages': total_pages,
                'next_page_url': next_page_url
            }
        except Exception as e:
            if isinstance(e, (ContentNotLoadedException, DataComponentNotFoundException)):
                raise
            raise DataParsingException(
                f"Failed to parse pagination details in JayWalking for {page_url}: {str(e)}"
            ) from e

    def get_product_listings(self, listings_page_url, page = 1):
        try:
            page_content = self.get_page_content(listings_page_url)
            soup = BeautifulSoup(page_content, "html.parser")
            product_links = []
            product_link_eles = soup.find_all("a", attrs={"class": "product-item__special-link"})

            for product_link in product_link_eles:
                href = product_link.get("href")
                if not href or "gift-card" in href:
                    continue
                product_links.append(self.base_url[:-1] + href)

            return product_links
        except Exception as e:
            if isinstance(e, ContentNotLoadedException):
                raise
            raise DataParsingException(
                f"Failed to parse product listings in JayWalking for {listings_page_url}: {str(e)}"
            ) from e

    def _extract_title(self, soup: BeautifulSoup) -> str:
        try:
            title_element = soup.find("h1", attrs={"class": "product-title"})
            if not title_element:
                raise DataComponentNotFoundException(
                    "Failed to find data component for product title in JayWalking."
                )

            title = title_element.get_text(strip=True)
            if not title:
                raise DataParsingException("Failed to parse product title in JayWalking.")

            return title
        except Exception as e:
            if isinstance(e, (DataComponentNotFoundException, DataParsingException)):
                raise
            raise DataParsingException(
                f"Failed to parse data for product title in JayWalking: {str(e)}"
            ) from e

    def _extract_id(self, soup: BeautifulSoup) -> str:
        try:
            title = self._extract_title(soup)
            title_parts = title.lower().split()
            product_id = self.id_prefix + "_".join(title_parts[:-1])

            if not product_id or product_id == self.id_prefix:
                raise DataParsingException("Failed to parse product ID in JayWalking.")

            return product_id
        except Exception as e:
            if isinstance(e, (DataComponentNotFoundException, DataParsingException)):
                raise
            raise DataParsingException(
                f"Failed to parse data for product ID in JayWalking: {str(e)}"
            ) from e

    def _extract_category(self, soup: BeautifulSoup) -> str:
        return "Dummy String"

    def _extract_price(self, soup: BeautifulSoup) -> float:
        try:
            price = soup.find("span", attrs={"class": "product-price"})
            if price is None:
                raise DataComponentNotFoundException(
                    "Failed to find data component for price in JayWalking."
                )

            return float(price.text.split()[-1].replace(",", ""))
        except DataComponentNotFoundException as e:
            raise e
        except Exception as e:
            raise DataParsingException(
                f"Failed to parse data for price in JayWalking: {str(e)}"
            ) from e

    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        try:
            sizes_labels = soup.find_all("label", attrs={"class": "product-variant__label"})
            if not sizes_labels:
                raise DataComponentNotFoundException(
                    "Failed to find data component for sizes in JayWalking."
                )

            sizes = []
            for size_label in sizes_labels:
                size_text = size_label.get_text(strip=True)
                if size_text:
                    sizes.append(size_text)

            return sizes
        except DataComponentNotFoundException as e:
            raise e
        except Exception as e:
            raise DataParsingException(
                f"Failed to parse data for sizes in JayWalking: {str(e)}"
            ) from e

    def _extract_description(self, soup: BeautifulSoup) -> str:
        try:
            description_container = soup.find("div", class_="rte")
            if not description_container:
                raise DataComponentNotFoundException(
                    "Failed to find data component for description in JayWalking."
                )

            size_chart_table = description_container.find("table")
            if size_chart_table:
                size_chart_table.decompose()

            size_chart_heading = description_container.find(
                string=lambda text: text and "SIZE CHART" in text.upper()
            )
            if size_chart_heading:
                size_chart_heading.parent.decompose()

            description_text = description_container.get_text(separator=" ", strip=True)
            if not description_text:
                raise DataParsingException(
                    "Failed to parse data for description in JayWalking."
                )

            return description_text.lower().capitalize()
        except DataComponentNotFoundException as e:
            raise e
        except Exception as e:
            raise DataParsingException(
                f"Failed to parse data for description in JayWalking: {str(e)}"
            ) from e

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
        except Exception as e:
            raise DataParsingException(
                f"Failed to parse data for material in JayWalking: {str(e)}"
            ) from e

    def _extract_image_url(self, soup: BeautifulSoup) -> list:
        try:
            product_gallery_items = soup.find_all(
                "div", attrs={"class": "product-gallery-item"}
            )
            if not product_gallery_items:
                raise DataComponentNotFoundException(
                    "Failed to find data component for image in JayWalking."
                )

            img = product_gallery_items[0].find("img")
            if img is None or not img.get("src"):
                raise DataComponentNotFoundException(
                    "Failed to find image source in JayWalking."
                )

            return "https:" + img["src"]
        except DataComponentNotFoundException as e:
            raise e
        except Exception as e:
            raise DataParsingException(
                f"Failed to parse data for image in JayWalking: {str(e)}"
            ) from e

    def _extract_gender(self, soup: BeautifulSoup) -> str:
        try:
            title = self._extract_title(soup).lower()
            if 'unisex' in title:
                return "Unisex"
            else:
                return "Woman"
        except DataComponentNotFoundException as e:
            raise e
        except Exception as e:
            raise DataParsingException(
                f"Failed to parse data for gender in JayWalking: {str(e)}"
            ) from e

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
            body_content = soup.body.prettify() if soup.body else page_content
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
                page_content=body_content
            )
            return product
        except Exception as e:
            if isinstance(
                e,
                (
                    DataComponentNotFoundException,
                    DataParsingException,
                    ContentNotLoadedException,
                ),
            ):
                raise
            raise DataParsingException(
                f"Error extracting product details from {product_page_url}: {str(e)}"
            ) from e

    def close(self):
        if self.content_loader:
            self.content_loader.close()
