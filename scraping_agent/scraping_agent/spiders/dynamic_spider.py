"""
Sample Run Command:

Amazon

scrapy crawl dynamic_spider \
-a urls='["https://www.amazon.in/s?k=shoes"]' \
-a selectors='{
  "product": {
    "product_container": {
      "type": "element",
      "selector": "//div[contains(@class, \"s-main-slot s-result-list\")]//div[contains(@class, \"puis-card-container \")]"
    },
    "info": {
      "title": {
        "type": "text",
        "selector": ".//div[contains(@data-cy, \"title-recipe\")]/a/h2/span/text()"
      },
      "price": {
        "type": "text",
        "selector": ".//span[contains(@class, \"price-whole\")]/text()"
      }
    }
  }
}' \
-a job_id="job_amazon_scrape"
"""

import json
import scrapy
from datetime import datetime
from urllib.parse import urljoin

class DynamicSpider(scrapy.Spider):
    name = 'dynamic_spider'

    def __init__(self, urls=None, selectors=None, job_id=None, *args, **kwargs):
        super(DynamicSpider, self).__init__(*args, **kwargs)

        self.start_urls = json.loads(urls) if urls else []
        self.selectors = json.loads(selectors) if selectors else {}
        self.job_id = job_id
        self.results = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            item = {
                "url": response.url,
                "timestamp": datetime.now().isoformat(),
                "data": [],
            }

            extracted_data = []

            product_container_selector = self.selectors.get("product", {}).get("product_container", {}).get("selector", "")
            product_containers = response.xpath(product_container_selector)

            for container in product_containers:
                product_data = {}

                for field, config in self.selectors.get("product", {}).get("info", {}).items():
                    selector = config.get("selector", "")
                    field_type = config.get("type", "text")
                    values = container.xpath(selector).getall()

                    if field_type == "url" or field_type == "image":
                        values = [urljoin(response.url, v) for v in values]

                    product_data[field] = values if values else None

                if self.is_valid_product(product_data):
                    extracted_data.append(product_data)

            for index, data in enumerate(extracted_data, start=1):
                data["page_rank"] = index

            if extracted_data:
                item["data"] = extracted_data
                self.results.append(item)

            return item

        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {str(e)}")
            return {"url": response.url, "error": str(e), "timestamp": datetime.now().isoformat()}

    def is_valid_product(self, product_data):
        for field, value in product_data.items():
            if value is None or (isinstance(value, list) and not value) or (
                    isinstance(value, str) and not value.strip()):
                return False
        return True

    def closed(self, spider):
        if self.results:
            collected_items = len(self.results[0].get("data", []))
            self.logger.info(f"Collected {collected_items} items")
        print(json.dumps(self.results, indent=4))
