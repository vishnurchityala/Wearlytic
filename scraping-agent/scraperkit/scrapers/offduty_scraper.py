import json
import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup

from scraperkit.base import BaseScraper
from scraperkit.exceptions import (
    ContentNotLoadedException,
    DataComponentNotFoundException,
    DataParsingException,
)
from scraperkit.loaders import SeleniumContentLoader
from scraperkit.models import Product


class OffDutyScraper(BaseScraper):
    """
    OffDutyScraper extracts structured product data from offduty.in listing and
    product pages. OffDuty uses a Shopify theme whose collection grid is rendered
    into product-card elements, so the scraper intentionally scopes listing
    extraction to the collection product grid.
    """

    def __init__(self, headers=None, content_loader=None):
        super().__init__("https://offduty.in/", headers=headers or {})
        self.id_prefix = "offduty_"
        self.content_loader = content_loader or SeleniumContentLoader(headers=headers)
        self._current_listing_url = None

    def get_page_content(self, page_url):
        try:
            page_content = self.content_loader.load_content(page_url=page_url)
            if not page_content:
                raise ContentNotLoadedException(
                    f"Failed to retrieve OffDuty page content: {page_url}"
                )
            return page_content
        except Exception as exc:
            if isinstance(exc, ContentNotLoadedException):
                raise
            raise ContentNotLoadedException(
                f"Error while loading OffDuty page content: {page_url}"
            ) from exc

    def _get_listing_page_content(self, page_url):
        if page_url == self._current_listing_url and self.current_page_content:
            return self.current_page_content

        page_content = self.get_page_content(page_url)
        self._current_listing_url = page_url
        self.current_page_content = page_content
        return page_content

    def get_pagination_details(self, page_url):
        try:
            page_content = self._get_listing_page_content(page_url)
            soup = BeautifulSoup(page_content, "html.parser")
            current_page = self._extract_current_page_number(page_url)
            pagination_links = self._extract_pagination_links(soup)

            return {
                "current_page": current_page,
                "total_pages": self._extract_total_pages(
                    pagination_links=pagination_links,
                    current_page=current_page,
                ),
                "next_page_url": self._extract_next_page_url(
                    page_url=page_url,
                    pagination_links=pagination_links,
                    current_page=current_page,
                ),
            }
        except Exception as exc:
            if isinstance(exc, ContentNotLoadedException):
                raise
            raise DataParsingException(
                f"Error parsing OffDuty pagination details from {page_url}: {exc}"
            ) from exc

    def _extract_current_page_number(self, page_url):
        page_values = parse_qs(urlparse(page_url).query).get("page")
        if not page_values:
            return 1

        try:
            return max(int(page_values[0]), 1)
        except (TypeError, ValueError):
            return 1

    def _extract_pagination_links(self, soup):
        roots = []
        seen_roots = set()

        def add_root(root):
            if root and id(root) not in seen_roots:
                roots.append(root)
                seen_roots.add(id(root))

        for root in soup.select(".pagination-wrapper, .pagination"):
            add_root(root)

        for nav in soup.find_all("nav"):
            nav_text = " ".join(
                [
                    " ".join(nav.get("class", [])),
                    nav.get("aria-label", ""),
                    nav.get("role", ""),
                ]
            ).lower()
            if "pagination" in nav_text:
                add_root(nav)

        links = []
        seen_links = set()
        search_roots = roots or [soup.find("main") or soup]

        for root in search_roots:
            for link in root.find_all("a", href=True):
                if "page=" not in link["href"] and not link.get_text(" ", strip=True).isdigit():
                    continue

                link_key = (link.get("href"), link.get_text(" ", strip=True))
                if link_key in seen_links:
                    continue

                links.append(link)
                seen_links.add(link_key)

        return links

    def _extract_total_pages(self, pagination_links, current_page):
        page_numbers = [current_page]
        for link in pagination_links:
            page_number = self._extract_page_number_from_link(link)
            if page_number is not None:
                page_numbers.append(page_number)

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

    def get_product_listings(self, listings_page_url, page=1):
        try:
            page_content = self._get_listing_page_content(listings_page_url)
            soup = BeautifulSoup(page_content, "html.parser")

            product_grid = soup.select_one("ul.product-grid")
            if not product_grid:
                raise DataComponentNotFoundException(
                    f"OffDuty product grid not found on listing page: {listings_page_url}"
                )

            product_cards = product_grid.select("product-card.product-card, .product-card")
            if not product_cards:
                raise DataComponentNotFoundException(
                    f"OffDuty product cards not found on listing page: {listings_page_url}"
                )

            product_links = []
            seen_urls = set()
            for product_card in product_cards:
                product_link = self._extract_product_card_url(product_card)
                if not product_link or product_link in seen_urls:
                    continue

                product_links.append(product_link)
                seen_urls.add(product_link)

            if not product_links:
                raise DataParsingException(
                    f"Found OffDuty product cards on page {page} but extracted no product links"
                )

            return product_links
        except Exception as exc:
            if isinstance(
                exc,
                (
                    ContentNotLoadedException,
                    DataComponentNotFoundException,
                    DataParsingException,
                ),
            ):
                raise
            raise DataParsingException(
                f"Error parsing OffDuty product listings from {listings_page_url}: {exc}"
            ) from exc

    def _extract_product_card_url(self, product_card):
        link = product_card.select_one("a.product-card__link[href]")
        if not link:
            link = product_card.select_one("a[href*='/products/']")

        if not link:
            return None

        return self._normalize_product_url(link.get("href"))

    def _normalize_product_url(self, href):
        if not href or "/products/" not in href:
            return None

        absolute_url = urljoin(self.base_url, href)
        parsed = urlparse(absolute_url)
        if parsed.netloc not in {"offduty.in", "www.offduty.in"}:
            return None

        return parsed._replace(fragment="").geturl()

    def _extract_id(self, soup: BeautifulSoup, product_page_url=None) -> str:
        source_url = self._extract_canonical_product_url(soup) or product_page_url
        handle = urlparse(source_url or "").path.rstrip("/").split("/")[-1]
        if not handle:
            handle = self._extract_title(soup)

        normalized_handle = re.sub(r"[^a-z0-9]+", "_", handle.lower()).strip("_")
        if not normalized_handle:
            raise DataParsingException("Failed to parse OffDuty product ID")

        return f"{self.id_prefix}{normalized_handle}"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_element = soup.select_one(".product-information h1") or soup.find("h1")
        title = self._clean_text(title_element.get_text(" ", strip=True)) if title_element else None
        if not title:
            title = self._extract_meta_content(soup, "og:title", "twitter:title")

        if not title:
            raise DataComponentNotFoundException("OffDuty product title not found")

        return title

    def _extract_category(self, soup: BeautifulSoup) -> str | None:
        product_group = self._json_ld_by_type(soup, "ProductGroup")
        category = product_group.get("category") if product_group else None
        if category:
            return self._clean_text(str(category))

        product_url = self._extract_canonical_product_url(soup)
        path_parts = [part for part in urlparse(product_url or "").path.split("/") if part]
        if "collections" in path_parts:
            index = path_parts.index("collections")
            if len(path_parts) > index + 1:
                return path_parts[index + 1].replace("-", " ").title()

        return None

    def _extract_price(self, soup: BeautifulSoup) -> float:
        for key in ("og:price:amount", "product:price:amount"):
            price_text = self._extract_meta_content(soup, key)
            price = self._parse_price(price_text)
            if price:
                return price

        product_price = soup.select_one(".product-information product-price")
        price = self._parse_price(
            product_price.get_text(" ", strip=True) if product_price else None
        )
        if price:
            return price

        raise DataComponentNotFoundException("OffDuty product price not found")

    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        return self._extract_variant_values(soup, "Size")

    def _extract_description(self, soup: BeautifulSoup) -> str:
        details_description = self._extract_description_from_details(soup)
        if details_description:
            return details_description

        product_group = self._json_ld_by_type(soup, "ProductGroup")
        description = product_group.get("description") if product_group else None
        if not description:
            description = self._extract_meta_content(
                soup, "og:description", "twitter:description", "description"
            )

        description = self._clean_text(description)
        if not description:
            raise DataComponentNotFoundException("OffDuty product description not found")

        return description

    def _extract_material(self, soup: BeautifulSoup) -> str | None:
        description = self._extract_description(soup)
        patterns = [
            r"(?:composition|fabric)\s*:?\s*([^.;\n]+)",
            r"material(?:\s*&\s*care)?\s*:?\s*([^.;\n]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, description, flags=re.IGNORECASE)
            if not match:
                continue

            material = match.group(1)
            material = re.split(
                r"\b(?:product color|country of origin|wash|details|length|elasticity)\b",
                material,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0]
            material = self._clean_text(material)
            if material:
                return material

        return None

    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        image_url = self._extract_meta_content(
            soup, "og:image:secure_url", "og:image", "twitter:image"
        )
        if not image_url:
            product_group = self._json_ld_by_type(soup, "ProductGroup")
            image = product_group.get("image") if product_group else None
            if isinstance(image, list):
                image_url = image[0] if image else None
            elif isinstance(image, str):
                image_url = image

        image_url = self._normalize_asset_url(image_url)
        if not image_url:
            raise DataComponentNotFoundException("OffDuty product image not found")

        return image_url

    def _extract_gender(self, soup: BeautifulSoup) -> str | None:
        candidate = " ".join(
            filter(
                None,
                [
                    self._safe_extract(self._extract_title, soup),
                    self._safe_extract(self._extract_description, soup),
                    self._safe_extract(self._extract_category, soup),
                ],
            )
        ).lower()

        if re.search(r"\b(women|woman|womens|female)\b", candidate):
            return "Women"
        if re.search(r"\b(men|mens|male)\b", candidate):
            return "Men"

        return None

    def _extract_colors(self, soup: BeautifulSoup) -> list:
        return self._extract_variant_values(soup, "Color")

    def _extract_rating(self, soup: BeautifulSoup) -> float:
        aggregate_rating = self._extract_aggregate_rating(soup)
        if aggregate_rating and aggregate_rating.get("ratingValue") is not None:
            try:
                return float(aggregate_rating["ratingValue"])
            except (TypeError, ValueError):
                pass

        badge = soup.select_one(".jdgm-prev-badge")
        badge_text = badge.get_text(" ", strip=True) if badge else ""
        match = re.search(r"(\d+(?:\.\d+)?)", badge_text)
        return float(match.group(1)) if match else 0.0

    def _extract_review_count(self, soup: BeautifulSoup) -> int:
        aggregate_rating = self._extract_aggregate_rating(soup)
        if aggregate_rating and aggregate_rating.get("reviewCount") is not None:
            return self._parse_count(aggregate_rating["reviewCount"])

        badge = soup.select_one(".jdgm-prev-badge")
        badge_text = badge.get_text(" ", strip=True) if badge else ""
        match = re.search(r"\(([^)]+)\)", badge_text)
        return self._parse_count(match.group(1)) if match else 0

    def get_product_details(self, product_page_url):
        try:
            page_content = self.get_page_content(product_page_url)
            soup = BeautifulSoup(page_content, "html.parser")
            body_content = soup.body.prettify() if soup.body else page_content
            scraped_at = datetime.now(timezone.utc)

            product = Product(
                id=self._extract_id(soup, product_page_url),
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
                page_content=body_content,
            )
            return product
        except Exception as exc:
            if isinstance(
                exc,
                (
                    ContentNotLoadedException,
                    DataComponentNotFoundException,
                    DataParsingException,
                ),
            ):
                raise
            raise DataParsingException(
                f"Error extracting OffDuty product details from {product_page_url}: {exc}"
            ) from exc

    def _extract_variant_values(self, soup, option_name):
        values = []
        seen_values = set()
        normalized_option = option_name.lower()

        for fieldset in soup.find_all("fieldset"):
            fieldset_text = fieldset.get_text(" ", strip=True).lower()
            fieldset_input_names = " ".join(
                input_tag.get("name", "")
                for input_tag in fieldset.find_all(["input", "option"])
            ).lower()
            if normalized_option not in f"{fieldset_text} {fieldset_input_names}":
                continue

            for input_tag in fieldset.find_all(["input", "option"]):
                if input_tag.has_attr("disabled") or input_tag.get("aria-disabled") == "true":
                    continue

                value = input_tag.get("value") or input_tag.get_text(" ", strip=True)
                value = self._clean_text(value)
                if not value or value.lower() == "on" or value.lower() in seen_values:
                    continue

                values.append(value)
                seen_values.add(value.lower())

        return values

    def _extract_description_from_details(self, soup):
        for details in soup.select(".product-information details, details.details"):
            summary = details.find("summary")
            summary_text = self._clean_text(
                summary.get_text(" ", strip=True) if summary else ""
            )
            details_text = self._clean_text(details.get_text(" ", strip=True))

            if "description" not in f"{summary_text} {details_text}".lower():
                continue

            if details_text.lower().startswith("description"):
                details_text = details_text[len("description"):].strip()

            if details_text:
                return details_text

        return None

    def _extract_canonical_product_url(self, soup):
        canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
        if canonical and canonical.get("href"):
            return canonical["href"]

        return self._extract_meta_content(soup, "og:url")

    def _extract_aggregate_rating(self, soup):
        product = self._json_ld_by_type(soup, "Product")
        aggregate_rating = product.get("aggregateRating") if product else None
        return aggregate_rating if isinstance(aggregate_rating, dict) else None

    def _json_ld_by_type(self, soup, target_type):
        for item in self._json_ld_objects(soup):
            item_type = item.get("@type")
            if item_type == target_type:
                return item
            if isinstance(item_type, list) and target_type in item_type:
                return item

        return None

    def _json_ld_objects(self, soup):
        objects = []
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw_json = script.string or script.get_text()
            if not raw_json:
                continue

            try:
                data = json.loads(raw_json)
            except json.JSONDecodeError:
                continue

            objects.extend(self._flatten_json_ld(data))

        return objects

    def _flatten_json_ld(self, data):
        if isinstance(data, dict):
            flattened = [data]
            graph = data.get("@graph")
            if isinstance(graph, list):
                for item in graph:
                    flattened.extend(self._flatten_json_ld(item))
            return flattened

        if isinstance(data, list):
            flattened = []
            for item in data:
                flattened.extend(self._flatten_json_ld(item))
            return flattened

        return []

    def _extract_meta_content(self, soup, *keys):
        for key in keys:
            tag = (
                soup.find("meta", attrs={"property": key})
                or soup.find("meta", attrs={"name": key})
                or soup.find("meta", attrs={"itemprop": key})
            )
            if tag and tag.get("content"):
                return self._clean_text(tag["content"])

        return None

    def _normalize_asset_url(self, value):
        if not value:
            return None

        value = self._clean_text(value)
        if value.startswith("//"):
            return f"https:{value}"
        if value.startswith("/"):
            return urljoin(self.base_url, value)

        return value

    def _parse_price(self, value):
        if value is None:
            return None

        text = self._clean_text(str(value))
        match = re.search(r"(\d[\d,]*(?:\.\d+)?)", text)
        if not match:
            return None

        try:
            price = float(match.group(1).replace(",", ""))
        except ValueError:
            return None

        return price if price > 0 else None

    def _parse_count(self, value):
        text = self._clean_text(str(value)).replace(",", "").lower()
        match = re.search(r"(\d+(?:\.\d+)?)([km]?)", text)
        if not match:
            return 0

        count = float(match.group(1))
        suffix = match.group(2)
        if suffix == "k":
            count *= 1000
        elif suffix == "m":
            count *= 1000000

        return int(count)

    def _safe_extract(self, extractor, soup):
        try:
            return extractor(soup)
        except Exception:
            return None

    def _clean_text(self, value):
        if value is None:
            return None

        text = unescape(str(value)).replace("\xa0", " ")
        return re.sub(r"\s+", " ", text).strip()

    def close(self):
        if self.content_loader:
            self.content_loader.close()
