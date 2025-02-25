from datetime import datetime

import scrapy
from scrapy_playwright.page import PageMethod

class SouledStoreSpider(scrapy.Spider):
    name = "souledstore_spider"
    start_urls = ["https://www.thesouledstore.com/search?q=T-Shirts&page=1"]

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,  # 60 seconds timeout
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("evaluate", """
                            async () => {
                                let lastHeight = 0;
                                while (document.body.scrollHeight > lastHeight) {
                                    lastHeight = document.body.scrollHeight;
                                    window.scrollTo(0, lastHeight);
                                    await new Promise(resolve => setTimeout(resolve, 2000));  // Wait for new items
                                }
                            }
                        """),
                        PageMethod("wait_for_selector", "div.pro-list")
                    ]
                },
                callback=self.parse,
            )

    def parse(self, response):
        product_links = response.xpath("//div[contains(@class, 'productlist')]//a/@href").getall()

        if not product_links:
            yield scrapy.Request(
                response.url,
                meta={"playwright": True,
                      "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")]},
                callback=self.parse,
                dont_filter=True
            )
            return

        for link in product_links:
            product_url = response.urljoin(link)
            yield scrapy.Request(
                product_url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")]
                },
                callback=self.parse_product
            )

    def parse_product(self, response):
        timestamp = datetime.utcnow().timestamp()

        # Extract price
        rupee_symbol = response.xpath("//span[contains(@class, 'irupee')]/text()").get()
        price_value = response.xpath("//span[contains(@class, 'fbold') and contains(@style, 'font-size')]/text()").get()
        price = f"{rupee_symbol}{price_value.strip()}" if price_value else None

        # Extract all sizes (both in-stock and out-of-stock)
        sizes = response.xpath("//ul[contains(@class, 'sizelist')]//li//label/span/text()").getall()

        # Extract material & care details
        details = response.xpath("//div[contains(@class, 'card-block')]/p/div/div/text()").getall()
        details_cleaned = [detail.strip() for detail in details if detail.strip()]

        material_and_care = []
        for index, text in enumerate(details_cleaned):
            if "Material & Care" in text and index + 2 < len(details_cleaned):
                material_and_care.append(details_cleaned[index + 1])
                material_and_care.append(details_cleaned[index + 2])

        # Extract description
        description = response.xpath(
            "//div[@id='collapseTwo']//div[contains(@class, 'card-block')]/p/span/text()").get()

        # Extract category
        category = response.xpath("//h1[contains(@class, 'prod-cat')]/text()").get()

        item = {
            "timestamp": timestamp,
            "source": "thesouledstore.com",
            "product_url": response.url,
            "product_name": response.xpath("//h1[contains(@class, 'title-size')]/text()").get(),
            "brand": "The Souled Store",
            "category": category.strip() if category else None,
            "description": description.strip() if description else None,
            "price": price,
            "sizes": sizes,
            "colors": response.xpath("//div[contains(@class, 'color-options')]/span/@title").getall(),
            "material": material_and_care,
            "image_url": response.xpath("//img[contains(@class, 'minProd')]/@src").get()
        }

        yield item
