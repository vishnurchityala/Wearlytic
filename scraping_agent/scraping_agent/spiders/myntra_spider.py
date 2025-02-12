import scrapy
from scrapy_playwright.page import PageMethod
import time

class MyntraSpider(scrapy.Spider):
    name = "myntra_spider"
    allowed_domains = ["myntra.com"]

    start_urls = [
        "https://www.myntra.com/oversized-tshirts"
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
        product_links = response.css("li.product-base a::attr(href)").getall()
        for link in product_links:
            product_url = response.urljoin(link)
            yield scrapy.Request(
                product_url,
                meta={"playwright": True,
                      "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")]},
                callback=self.parse_product
            )

        next_page = response.css("a.pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        yield {
            "timestamp": time.time(),
            "source": "myntra.com",
            "product_url": response.url,
            "product_name": response.css("h1.pdp-name::text").get(),
            "brand": response.css("h1.pdp-title::text").get(),
            "category": response.css("div.breadcrumbs-container a.breadcrumbs-link:nth-last-of-type(3)::text").get(),
            "description": response.css(".pdp-product-description-content::text").get(),
            "price": response.css("span.pdp-price strong::text").get(),
            "colors": response.css(".pdp-color-options-container img::attr(alt)").getall(),
            "material": response.css(".pdp-material-composition::text").get(),
            "image_url": response.css(".image-grid img::attr(src)").get(),
        }
