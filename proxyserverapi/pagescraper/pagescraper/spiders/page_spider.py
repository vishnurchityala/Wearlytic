import scrapy
from scrapy_splash import SplashRequest

class PageSpider(scrapy.Spider):
    name = 'page_spider'

    def __init__(self, url='', *args, **kwargs):
        super(PageSpider, self).__init__(*args, **kwargs)
        self.url = url

    def start_requests(self):
        # Start request with the URL passed as argument
        yield SplashRequest(
            self.url,
            callback=self.parse,
            args={'wait': 10, 'timeout': 60},
            splash_headers={'Accept-Language': 'en-US,en;q=0.9',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )

    def parse(self, response):
        # Get the full page source
        page_source = response.body.decode('utf-8')
        self.log(f"Page Source: {page_source[:100]}...")  # Log first 100 characters

        # Return the page source as output
        yield {
            'url': response.url,
            'content': page_source,
        }
