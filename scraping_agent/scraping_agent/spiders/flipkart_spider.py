import scrapy
from datetime import datetime
import re


class FlipkartSpider(scrapy.Spider):
    name = "flipkart_spider"
    allowed_domains = ["flipkart.com"]

    start_urls = [
        f"https://www.flipkart.com/search?q={category}&page={i}"
        for category in ["tshirts"]
        for i in range(1, 2)
    ]

    def parse(self, response):
        product_links = response.xpath("//a[contains(@class, 'WKTcLC')]/@href").getall()

        if not product_links:
            yield scrapy.Request(
                response.url,
                callback=self.parse,
                dont_filter=True
            )
            return

        for link in product_links:
            product_url = response.urljoin(link)
            yield scrapy.Request(
                product_url,
                callback=self.parse_product
            )

    def parse_product(self, response):
        timestamp = datetime.utcnow().timestamp()

        breadcrumb_links = response.xpath("//div[contains(@class, '_7dPnhA')]/div/a")

        item = {
            "timestamp": timestamp,
            "source": "flipkart.com",
            "product_url": response.url,
            "product_name": response.xpath("//div[contains(@class, 'aL22KS')]/div/p/text()").get(),
            "brand": response.xpath("//span[contains(@class, 'mEh187')]/text()").get(),
            "category": breadcrumb_links[-3].xpath("text()").get() if len(breadcrumb_links) >= 3 else None,
            "description": response.xpath("//span[contains(@class, 'VU-ZEz')]/text()").get(),
            "price": response.xpath("//div[contains(@class, 'Nx9bqj CxhGGd')]/text()").get(),
            "material": response.xpath("//div[contains(@class, 'col col-9-12 -gXFvC')]/text()").get(),
            "image_url": response.xpath("//div[contains(@class, 'gqcSqV YGE0gZ')]/img/@src").get()
        }

        print(item)
        yield item

