import scrapy
from scrapy_playwright.page import PageMethod
import time

class HMSpider(scrapy.Spider):
    name = "hm_spider"
    allowed_domains = ["hm.com"]

    start_urls = [
        "https://www2.hm.com/en_in/men/shop-by-product/tshirts-tank-tops.html"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")]
                },
                callback=self.parse
            )

    def parse(self, response):
        product_links = response.css("li.product-item a::attr(href)").getall()
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

        next_page = response.css("a.pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        yield {
            "timestamp": time.time(),
            "source": "hm.com",
            "product_url": response.url,
            "product_name": response.css("h1.primary.product-item-headline::text").get(),
            "brand": "H&M",
            "category": response.css("nav.breadcrumb li:nth-last-of-type(3) a::text").get(),
            "description": response.css("p.pdp-description-text::text").get(),
            "price": response.css("span.price-value::text").get(),
            "colors": response.css(".product-input-label span::text").getall(),
            "material": response.css(".composition-list-item::text").get(),
            "image_url": response.css(".product-detail-thumbnail img::attr(src)").get(),
        }
