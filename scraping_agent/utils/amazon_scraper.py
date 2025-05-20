from bs4 import BeautifulSoup
from base_scraper import BaseScraper
from selenium_content_loader import SeleniumContentLoader


class AmazonScraper(BaseScraper):
    """
    AmazonScraper implementation of BaseScraper, scraping Amazon.in product info.
    """
    def __init__(self, headers=None,content_loader=None):
        super().__init__("https://www.amazon.in/", headers=headers)
        self.content_loader = content_loader or SeleniumContentLoader(headers=headers)

    def get_page_content(self, page_url):
        try:
            return self.content_loader.load_content(page_url)
        except Exception as e:
            print(f"Error fetching page content: {e}")
            return None

    def get_pagination_details(self, page_content):
        soup = BeautifulSoup(page_content, 'html.parser')
        pagination_info = {
            'current_page': None,
            'total_pages': None,
            'next_page_url': None
        }

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

    def get_product_listings(self, listings_page_url, page=1):
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

    def trim_product_url(self, url):
        if '?' in url:
            return url.split('?')[0]
        return url

    def extract_product_description(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        description_data = {
            'bullet_points': [],
            'fabric_composition': None,
            'care_instructions': None
        }

        bullet_list = soup.find('ul', {'class': 'a-unordered-list a-vertical a-spacing-small'})
        if bullet_list:
            for li in bullet_list.find_all('li'):
                bullet_text = li.get_text().strip()
                description_data['bullet_points'].append(bullet_text)

                if 'fabric composition' in bullet_text.lower() or 'cotton' in bullet_text.lower() or 'polyester' in bullet_text.lower():
                    description_data['fabric_composition'] = bullet_text

                if any(care_term in bullet_text.lower() for care_term in ['wash', 'iron', 'bleach', 'dry', 'tumble']):
                    description_data['care_instructions'] = bullet_text

        return description_data

    def extract_color_options(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        color_options = []
        color_swatches = soup.find_all('img', {'class': 'swatch-image'})
        for swatch in color_swatches:
            if 'alt' in swatch.attrs:
                color_name = swatch['alt']
                if color_name and color_name not in color_options:
                    color_options.append(color_name)
        return color_options

    def get_product_details(self, product_page_url):
        try:
            product_page_url = self.trim_product_url(product_page_url)
            page_content = self.get_page_content(product_page_url)
            if not page_content:
                print(f"Failed to retrieve content for product page: {product_page_url}")
                return {}

            soup = BeautifulSoup(page_content, 'html.parser')
            product_details = {}

            title_tag = soup.find('span', {'id': 'productTitle'})
            if title_tag:
                product_details['title'] = title_tag.text.strip()

            price_tag = soup.find('span', {'id': 'priceblock_ourprice'}) or soup.find('span', {'id': 'priceblock_dealprice'})
            if price_tag:
                product_details['price'] = price_tag.text.strip()

            rating_tag = soup.find('span', {'class': 'a-icon-alt'})
            if rating_tag:
                product_details['rating'] = rating_tag.text.strip()

            review_count_tag = soup.find('span', {'id': 'acrCustomerReviewText'})
            if review_count_tag:
                product_details['review_count'] = review_count_tag.text.strip()

            product_details['description'] = self.extract_product_description(page_content)
            product_details['colors'] = self.extract_color_options(page_content)

            return product_details

        except Exception as e:
            print(f"Error fetching product details: {e}")
            return {}

    def close(self):
        if self.content_loader:
            self.content_loader.close()

if __name__ == "__main__":
    print("** Creating Amazon Scraper **")
    scraper = AmazonScraper()

    search_url = "https://www.amazon.in/s?k=tshirts"

    html_content = scraper.get_page_content(search_url)

    if html_content:
        print(f"Successfully retrieved {len(html_content)} characters of HTML")

        pagination_details = scraper.get_pagination_details(html_content)
        print("\nPagination Details:")
        for key, value in pagination_details.items():
            print(f"{key}: {value}")

        product_links = scraper.get_product_listings(search_url)

        print("\nSample Product Links:")
        for i, link in enumerate(product_links[:5]):
            print(f"{i+1}. {link}")

        if product_links:
            product_url = scraper.trim_product_url(product_links[-1])
            product_details = scraper.get_product_details(product_url)

            print("\nProduct Details:")
            for key, value in product_details.items():
                print(f"{key}: {value}")

    else:
        print("Failed to retrieve content")

    scraper.close()
