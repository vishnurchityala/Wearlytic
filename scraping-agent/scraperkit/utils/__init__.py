import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from scraperkit.exceptions import BadURLException
from .scraper_lru_cache import ScraperLRUCache

cache = ScraperLRUCache(max_size=17)

def extract_domain(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc or parsed_url.path
    if host.startswith("www."):
        host = host[4:]
    parts = host.split('.')
    if len(parts) >= 2:
        return parts[-2]
    else:
        return host

def get_scraper_from_url(url: str):
    """
    TODO: Refactor the domain-to-scraper class mapping logic to directly check for the specific domain instead of using an iterative search.
    """
    from scraperkit import SCRAPER_URL_MAP
    domain = extract_domain(url)
    scraper_class = SCRAPER_URL_MAP.get(domain,None)
    if scraper_class:
        scraper = cache.get(domain)
        if scraper:
            return scraper
        else:
            return scraper_class()
    else:
        raise BadURLException()

def get_driver_path():
    load_dotenv()
    platform = os.getenv("PLATFORM")
    if platform == 'macosarm64':
        return "./scraperkit/drivers/chromedriver-mac-arm64/chromedriver"
    elif platform == 'macosamd64':
        return "./scraperkit/drivers/chromedriver-mac-x64/chromedriver"
    elif platform == 'win64':
        return "./scraperkit/drivers/chromedriver-win64/chromedriver.exe"
