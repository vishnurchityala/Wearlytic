import scrapy
from scrapy_playwright.page import PageMethod
from datetime import datetime
import re


class MyntraSpider(scrapy.Spider):
    name = "myntra_spider"
    allowed_domains = ["myntra.com"]

    start_urls = [
        f"https://www.myntra.com/{category}?p={i}"
        for category in
        [
            # "tshirts","oversized-tshirts", "shirts"
            #  "jeans", "trousers", "jackets"
            "sweatshirts", "shorts", "dresses"
         ]
        for i in range(1, 3)
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True,
                      "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")]},
                callback=self.parse
            )

    def parse(self, response):
        product_links = response.xpath("//li[@class='product-base']/a/@href").getall()
        for link in product_links:
            product_url = response.urljoin(link)
            yield scrapy.Request(
                product_url,
                meta={"playwright": True,
                      "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")]},
                callback=self.parse_product
            )

    def parse_product(self, response):
        image_style = response.xpath("//div[@class='image-grid-image']/@style").get()
        image_url = None

        if image_style:
            match = re.search(r'url\("(.+?)"\)', image_style)
            if match:
                image_url = match.group(1)

        material = response.xpath("//div[contains(text(), 'Fabric')]/following-sibling::div/text()").get()

        timestamp = datetime.utcnow().timestamp()

        item = {
            "timestamp": timestamp,
            "source": "myntra.com",
            "product_url": response.url,
            "product_name": response.xpath(
                "//div[@class='breadcrumbs-container']//a[contains(@class, 'breadcrumbs-link')][last()-1]/text()").get(),
            "brand": response.xpath("//h1[contains(@class, 'pdp-title')]/text()").get(),
            "category": response.xpath(
                "//div[@class='breadcrumbs-container']//a[contains(@class, 'breadcrumbs-link')][last()-2]/text()").get(),
            "description": response.xpath("//h1[contains(@class, 'pdp-name')]/text()").get(),
            "price": response.xpath("//span[contains(@class, 'pdp-price')]//strong/text()").get(),
            "colors": response.xpath("//div[@class='pdp-color-options-container']//img/@alt").getall(),
            "material": material,
            "image_url": image_url,
        }
        print(item)
        yield item
