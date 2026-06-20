from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import parse_qs, urljoin, urlparse
from scraperkit.base import BaseScraper
from scraperkit.loaders import SeleniumContentLoader
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
        self.content_loader = content_loader or SeleniumContentLoader(headers=headers)
        self._current_listing_url = None
    
    def get_page_content(self, page_url):
        try:
            content = self.content_loader.load_content(page_url=page_url)
            return content
        except Exception as e:
            if isinstance(e, ContentNotLoadedException):
                raise
            raise ContentNotLoadedException(
                f"Error while loading page content of page url: {page_url}"
            ) from e

    def _get_listing_page_content(self, page_url):
        if page_url == self._current_listing_url and self.current_page_content:
            return self.current_page_content

        page_content = self.get_page_content(page_url)
        if not page_content:
            raise ContentNotLoadedException(
                f"Failed to retrieve listing page content from BluOrng: {page_url}"
            )

        self._current_listing_url = page_url
        self.current_page_content = page_content
        return page_content
    
    def get_pagination_details(self, page_url):
        page_content = self._get_listing_page_content(page_url)
        soup = BeautifulSoup(page_content, "html.parser")
        current_page = self._extract_current_page_number(page_url)
        pagination_links = self._extract_pagination_links(soup)

        return {
                'current_page': current_page,
                'total_pages': self._extract_total_pages(
                    pagination_links=pagination_links,
                    current_page=current_page,
                ),
                'next_page_url': self._extract_next_page_url(
                    page_url=page_url,
                    pagination_links=pagination_links,
                    current_page=current_page,
                )
            }

    def _extract_current_page_number(self, page_url):
        page_values = parse_qs(urlparse(page_url).query).get("page")
        if not page_values:
            return 1

        try:
            current_page = int(page_values[0])
        except (TypeError, ValueError):
            return 1

        return max(current_page, 1)

    def _extract_pagination_links(self, soup):
        pagination_roots = []
        seen_roots = set()

        def add_root(root):
            if not root or id(root) in seen_roots:
                return

            pagination_roots.append(root)
            seen_roots.add(id(root))

        for root in soup.select(".pagination-wrapper, .pagination"):
            add_root(root)

        for nav in soup.find_all("nav"):
            nav_class = " ".join(nav.get("class", []))
            nav_label = nav.get("aria-label", "")
            if "pagination" in f"{nav_class} {nav_label}".lower():
                add_root(nav)

        links = []
        seen_links = set()
        for root in pagination_roots:
            for link in root.find_all("a", href=True):
                link_key = (link.get("href"), link.get_text(" ", strip=True))
                if link_key in seen_links:
                    continue

                links.append(link)
                seen_links.add(link_key)

        if links:
            return links

        return [
            link for link in soup.find_all("a", href=True)
            if "page=" in link["href"]
        ]

    def _extract_total_pages(self, pagination_links, current_page):
        page_numbers = [current_page]
        for link in pagination_links:
            text = link.get_text(" ", strip=True)
            if text.isdigit():
                page_numbers.append(int(text))

        return max(page_numbers)

    def _extract_next_page_url(self, page_url, pagination_links, current_page):
        next_candidates = []

        for link in pagination_links:
            href = link.get("href")
            page_number = self._extract_page_number_from_link(link)
            if not href or page_number is None or page_number <= current_page:
                continue

            next_candidates.append((page_number, urljoin(page_url, href)))

        if not next_candidates:
            return None

        return min(next_candidates, key=lambda candidate: candidate[0])[1]

    def _extract_page_number_from_link(self, link):
        text = link.get_text(" ", strip=True)
        if text.isdigit():
            return int(text)

        page_values = parse_qs(urlparse(link.get("href", "")).query).get("page")
        if not page_values:
            return None

        try:
            return int(page_values[0])
        except (TypeError, ValueError):
            return None
    
    def get_product_listings(self, listings_page_url, page = 1):
        try:
            page_content = self._get_listing_page_content(listings_page_url)
            soup = BeautifulSoup(page_content,"html.parser")
            product_links = []
            product_cards = soup.find_all("div",attrs={"class":"card__content"})

            if not product_cards:
                raise DataComponentNotFoundException(f"Product Component Not Found in Listings Page : {listings_page_url}")
            try:
                for product_card in product_cards:
                    product_link_tag = product_card.find("a", href=True)
                    if not product_link_tag:
                        continue

                    product_link = self._normalize_product_listing_url(product_link_tag["href"])
                    if not product_link:
                        continue

                    if product_link not in product_links:
                        product_links.append(product_link)
            except Exception as e:
                raise DataParsingException(f"Error parsing product card from {listings_page_url}")

            if not product_links:
                raise DataParsingException(f"Found BluOrng product cards on page {page} but extracted no product links")
            
            return product_links
        
        except Exception as e:
            if isinstance(e, (DataComponentNotFoundException, ContentNotLoadedException)):
                            raise
            raise DataParsingException(f"Error parsing product listings from {listings_page_url}: {str(e)}")

    def _normalize_product_listing_url(self, href):
        if not href:
            return None

        absolute_url = urljoin(self.base_url, href)
        parsed_url = urlparse(absolute_url)
        host = parsed_url.netloc.lower()
        if host.startswith("www."):
            host = host[4:]

        if host != "bluorng.com" or not parsed_url.path.startswith("/products/"):
            return None

        return parsed_url._replace(
            scheme="https",
            netloc="bluorng.com",
            query="",
            fragment="",
        ).geturl()
    
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
            sizes_components = soup.find_all("input", attrs={"name": "Size"})
            if not sizes_components:
                sizes_div = soup.find("fieldset", attrs={"class": "js product-form__input"})
                if sizes_div:
                    sizes_components = sizes_div.find_all("input")

            sizes = []
            for size_component in sizes_components:
                size = size_component.get("value", "").strip()
                if size and size not in sizes:
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
            scraped_at = datetime.now(timezone.utc)
            
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
                scraped_datetime=scraped_at,
                processed_datetime=scraped_at,
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
