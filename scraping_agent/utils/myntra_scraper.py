import time
from bs4 import BeautifulSoup
from base_scraper import BaseScraper
from selenium_content_loader import SeleniumContentLoader

class MyntraScraper(BaseScraper):
    """
    MyntraScraper implementation of BaseScraper, scraping Amazon.in product info.
    """
    def __init__(self, headers=None):
        super().__init__("https://www.myntra.com/", headers=headers, content_loader=None)
        self.content_loader = SeleniumContentLoader(headers=headers)

    def get_page_content(self, page_url):
        try:
            return self.content_loader.load_content(page_url)
        except Exception as e:
            print(f"Error fetching page content from Myntra: {e}")
            return None

    def get_pagination_details(self, page_content):
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
                            import re
                            if 'p=' in current_url:
                                next_url = re.sub(r'p=\d+', f'p={current_page + 1}', current_url)
                            else:
                                if '?' in current_url:
                                    next_url = f"{current_url}&p={current_page + 1}"
                                else:
                                    next_url = f"{current_url}?p={current_page + 1}"
                            pagination_info['next_page_url'] = next_url
            return pagination_info
        except Exception as e:
            print(f"Error extracting pagination details: {e}")
            return pagination_info

    def get_product_listings(self, listings_page_url, page=1):
        if page > 1:
            if '?' in listings_page_url:
                url = f"{listings_page_url}&p={page}"
            else:
                url = f"{listings_page_url}?p={page}"
        else:
            url = listings_page_url
        page_content = self.get_page_content(url)
        if not page_content:
            print(f"Failed to retrieve content for page {page}")
            return []
        return self._extract_product_listings(page_content, page)

    def _extract_product_listings(self, page_content, page):
        soup = BeautifulSoup(page_content, 'html.parser')
        product_links = []
        product_items = soup.find_all('li', class_='product-base')
        for item in product_items:
            product_id = item.get('id')
            a_tag = item.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = 'https://www.myntra.com/' + href.lstrip('/')
                if full_url not in product_links:
                    product_links.append(full_url)
        print(f"Found {len(product_links)} unique product links on page {page}")
        return product_links

    def get_product_details(self, product_page_url):
        page_content = self.get_page_content(product_page_url)
        if not page_content:
            print(f"Failed to retrieve content for product page: {product_page_url}")
            return {}
        return self._extract_product_details(page_content)

    def _extract_product_details(self, page_content):
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            product_details = {
                'source': 'Myntra'
            }
            product_name = soup.find('h1', {'class': 'pdp-name'})
            if product_name:
                product_details['title'] = product_name.text.strip()
            brand_name = soup.find('h1', {'class': 'pdp-title'})
            if brand_name:
                product_details['brand'] = brand_name.text.strip()
            price = soup.find('span', {'class': 'pdp-price'})
            if price:
                product_details['price'] = price.text.strip()[1:]
            rating = soup.find('div', {'class': 'index-overallRating'})
            if rating:
                product_details['rating'] = rating.text.strip().split("|")[0]
                product_details['rating_count'] = rating.text.strip().split("|")[1].split()[0]
            description = soup.find('div', {'class': 'pdp-product-description-content'})
            if description:
                product_details['description'] = description.text.strip()
            sizes = []
            size_buttons = soup.find_all('div', {'class': 'size-buttons-size-button'})
            for size_button in size_buttons:
                size_text = size_button.text.strip()
                if size_text:
                    sizes.append(size_text)
            if sizes:
                product_details['available_sizes'] = sizes
            colors = [a["title"] for a in soup.select(".colors-container a") if a.has_attr("title")]
            if colors:
                product_details['colors'] = colors
            specifications = soup.select_one(".pdp-product-description-content")
            if specifications:
                product_details['description'] = specifications.get_text(separator=" ", strip=True)
            images = []
            image_containers = soup.find_all('div', {'class': 'image-grid-image'})
            for img_container in image_containers:
                img_tag = img_container.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    images.append(img_tag['src'])
            if images:
                product_details['images'] = images
            return product_details
        except Exception as e:
            print(f"Error extracting product details: {e}")
            return {}

    def close(self):
        if self.content_loader:
            self.content_loader.close()

if __name__ == "__main__":
    scraper = MyntraScraper(headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    })
    search_url = "https://www.myntra.com/tshirts"
    html_content = scraper.get_page_content(search_url)
    if html_content:
        print(f"Successfully retrieved {len(html_content)} characters of HTML")
        with open("myntra_results.html", "w+", encoding="utf-8") as file:
            file.write(html_content)
        pagination_details = scraper.get_pagination_details(html_content)
        print("\nPagination Details:")
        for key, value in pagination_details.items():
            print(f"{key}: {value}")
        product_links = scraper.get_product_listings(search_url)
        print("\nSample Product Links:")
        for i, link in enumerate(product_links[:5]):
            print(f"{i+1}. {link}")
        if product_links:
            product_url = product_links[0]
            product_details = scraper.get_product_details(product_url)
            print("\nProduct Details:")
            for key, value in product_details.items():
                print(f"{key}: {value}")
    else:
        print("Failed to retrieve content")
    scraper.close()
