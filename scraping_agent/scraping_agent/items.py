# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


import scrapy

class ProductItem(scrapy.Item):
    product_name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    image_url = scrapy.Field()
    product_url = scrapy.Field()
    colors = scrapy.Field()
    timestamp = scrapy.Field()
