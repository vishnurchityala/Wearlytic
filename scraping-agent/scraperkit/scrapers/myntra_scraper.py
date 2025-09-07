import time
from bs4 import BeautifulSoup
from scraperkit.base.base_scraper import BaseScraper
from scraperkit.loaders import SeleniumContentLoader
from scraperkit.models.product import Product
from scraperkit.exceptions import DataComponentNotFoundException, DataParsingException
from datetime import datetime, timezone

class MyntraScraper(BaseScraper):
    """
    MyntraScraper extracts structured product data from Myntra by parsing listing and product pages.
    It extends BaseScraper and returns results as Product objects.
    """
    def __init__(self, headers=None):
        super().__init__("https://www.myntra.com/", headers=headers)
        self.id_prefix = "mynt_"
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
        self.content_loader = SeleniumContentLoader(headers=self.headers, timeout=30)

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

    def _extract_id(self, soup: BeautifulSoup) -> str:
        try:
            id_element = soup.find('span',class_="supplier-styleId")
            if not id_element:
                raise DataComponentNotFoundException("ID element not found")
            
            id_text = id_element.text.strip()
            if not id_text:
                raise DataParsingException("ID text is empty")
            
            return f"{self.id_prefix}{id_text}"
        
        except Exception as e:
            raise e

    def _extract_title(self, soup: BeautifulSoup) -> str:
        try:
            product_name = soup.find('h1', {'class': 'pdp-name'})
            if not product_name:
                raise DataComponentNotFoundException("Title element not found")
            
            title = product_name.text.strip()
            if not title:
                raise DataParsingException("Title text is empty")
            
            return title
        except Exception as e:
            raise e

    def _extract_price(self, soup: BeautifulSoup) -> int:
        try:
            price = soup.find('span', {'class': 'pdp-price'})
            if not price:
                raise DataComponentNotFoundException("Price element not found")
            
            price_text = price.text.strip().replace('₹', '').replace(',', '')
            if not price_text:
                raise DataParsingException("Price text is empty")
            
            price_value = int(float(price_text))
            if price_value <= 0:
                raise DataParsingException(f"Invalid price value: {price_value}")
            
            return price_value
        except (ValueError, AttributeError) as e:
            raise DataParsingException(f"Error parsing price: {str(e)}")
        except Exception as e:
            raise e

    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        try:
            rating_container = soup.find('div', {'class': 'index-overallRating'})
            if not rating_container:
                return 0
            
            rating_div = rating_container.find('div')
            if not rating_div:
                raise DataParsingException("Rating div not found inside rating container")
            
            rating_text = rating_div.text.strip()
            if not rating_text:
                raise DataParsingException("Rating text is empty")
            
            rating_value = float(rating_text)
            if 0 <= rating_value <= 5:
                return rating_value
            else:
                raise DataParsingException(f"Invalid rating value: {rating_value}")
        
        except (ValueError, AttributeError) as e:
            raise DataParsingException(f"Error parsing rating: {str(e)}")
        except Exception as e:
            raise e

    def _extract_review_count(self, soup: BeautifulSoup) -> int | None:
        try:
            rating_container = soup.find('div', {'class': 'index-overallRating'})
            if not rating_container:
                return 0
            
            ratings_count = rating_container.find('div', {'class': 'index-ratingsCount'})
            if not ratings_count:
                return 0
            
            review_text = ratings_count.text.strip().split()[0].replace(',', '')
            if not review_text:
                raise DataParsingException("Review count text is empty")
            
            review_count = int(review_text)
            if review_count >= 0:
                return review_count
            else:
                raise DataParsingException(f"Invalid review count value: {review_count}")
        
        except (ValueError, AttributeError) as e:
            raise DataParsingException(f"Error parsing review count: {str(e)}")
        except Exception as e:
            raise e

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        try:
            descriptions_container = soup.find('div', class_='pdp-productDescriptorsContainer')
            if not descriptions_container:
                raise DataComponentNotFoundException("Description container not found.")
            
            description_p = descriptions_container.find('p', class_='pdp-product-description-content')
            if not description_p:
                raise DataComponentNotFoundException("Description paragraph not found.")
            
            list_items = description_p.find_all('li')
            if list_items:
                description = '\n'.join(item.get_text(strip=True) for item in list_items)
            else:
                description = description_p.get_text(strip=True)
            
            if not description:
                raise DataParsingException("Description text is empty.")

            return description
        
        except Exception as e:
            raise e

    def _extract_material(self, soup: BeautifulSoup) -> str | None:
        try:
            desc_sections = soup.find_all("div", class_="pdp-sizeFitDesc")
            if not desc_sections:
                raise DataComponentNotFoundException("No material section containers found.")
            
            for section in desc_sections:
                title = section.find("h4")
                if title and "material & care" in title.get_text(strip=True).lower():
                    content = section.find("p")
                    if not content:
                        raise DataComponentNotFoundException("Material & Care section found but no content <p> tag.")
                    
                    for br in content.find_all("br"):
                        br.replace_with("\n")
                    
                    material_text = content.get_text(strip=True)
                    if not material_text:
                        raise DataParsingException("Material & Care section is empty after parsing.")
                    
                    return material_text
            
            raise DataComponentNotFoundException("Material & Care section not found in the product description.")

        except Exception as e:
            raise e

    def _extract_sizes(self, soup: BeautifulSoup) -> list[str]:
        try:
            size_buttons = soup.find_all('button', class_='size-buttons-size-button')
            if not size_buttons:
                raise DataComponentNotFoundException("No size buttons found on the product page.")
            
            sizes = []
            for button in size_buttons:
                size_tag = button.find('p', class_='size-buttons-unified-size')
                if not size_tag or len(size_tag.contents) < 2:
                    continue
                
                size = size_tag.contents[1].strip()
                if not size:
                    raise DataParsingException("Empty size value found in a size button.")
                
                sizes.append(size)
            
            if not sizes:
                raise DataParsingException("Size buttons found but no valid sizes extracted.")
            
            return sizes

        except Exception as e:
            raise e
        
    def _extract_category(self, soup: BeautifulSoup) -> str | None:
        try:
            breadcrumb_container = soup.find('div', class_='breadcrumbs-container')
            if not breadcrumb_container:
                raise DataComponentNotFoundException("Breadcrumbs container not found.")

            links = breadcrumb_container.find_all('a', class_='breadcrumbs-link')
            if len(links) < 4:
                raise DataParsingException("Not enough breadcrumb links to extract category.")

            category = links[3].get_text(strip=True)
            if not category:
                raise DataParsingException("Extracted category is empty.")

            return category

        except Exception as e:
            raise e

    def _extract_gender(self, soup: BeautifulSoup) -> str | None:
        try:
            breadcrumb_container = soup.find('div', class_='breadcrumbs-container')
            if not breadcrumb_container:
                raise DataComponentNotFoundException("Breadcrumbs container not found.")

            links = breadcrumb_container.find_all('a', class_='breadcrumbs-link')

            if len(links) >= 3:
                gender_text = links[2].get_text(strip=True).split()[0]
                return gender_text if gender_text else None
            else:
                return None

        except Exception as e:
            raise e

    def _extract_colors(self, soup: BeautifulSoup) -> list[str]:
        try:
            colors_container = soup.find('div', class_='colors-container')
            if not colors_container:
                return []

            color_links = colors_container.find_all('a')
            colors = [link.get('title') for link in color_links if link.get('title')]
            return colors

        except Exception as e:
            return []

    def _extract_image_url(self, soup: BeautifulSoup) -> str | None:
        try:
            image_container = soup.find('div', class_='image-grid-imageContainer')
            if not image_container:
                raise DataComponentNotFoundException("Image container not found")

            image_div = image_container.find('div', class_='image-grid-image')
            if not image_div or 'style' not in image_div.attrs:
                raise DataComponentNotFoundException("Image div or style attribute not found")

            style = image_div['style']
            url_start = style.find('url("') + 5
            url_end = style.find('")', url_start)
            if url_start <= 4 or url_end <= url_start:
                raise DataParsingException("Failed to parse image URL from style attribute")

            image_url = style[url_start:url_end]
            if not image_url:
                raise DataParsingException("Extracted image URL is empty")

            return image_url
        
        except Exception as e:
            raise e

    def get_product_details(self, product_page_url: str) -> Product | dict:
        try:
            page_content = self.get_page_content(product_page_url)
            if not page_content:
                print(f"Failed to retrieve content for product page: {product_page_url}")
                return {}

            soup = BeautifulSoup(page_content, 'html.parser')
            body_content = soup.body.prettify()

            product_data = {
                'id': self._extract_id(soup),
                'title': self._extract_title(soup),
                'price': self._extract_price(soup),
                'rating': self._extract_rating(soup),
                'review_count': self._extract_review_count(soup),
                'description': self._extract_description(soup),
                'gender':self._extract_gender(soup),
                'category': self._extract_category(soup),
                'material': self._extract_material(soup),
                'sizes': self._extract_sizes(soup),
                'colors': self._extract_colors(soup),
                'image_url': self._extract_image_url(soup),
                'url': product_page_url,
                'processed': False,
                'scraped_datetime': datetime.now(timezone.utc).timestamp(),
                'processed_datetime': datetime.now(timezone.utc).timestamp(),
                'page_content': body_content
            }

            return Product(**product_data)

        except Exception as e:
            print(f"Error fetching product details: {e}")
            return {}

    def close(self):
        if self.content_loader:
            self.content_loader.close()