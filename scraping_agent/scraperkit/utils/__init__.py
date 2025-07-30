from urllib.parse import urlparse
from scraperkit import SCRAPER_URL_MAP

def get_scraper_from_url(url: str):
    domain = urlparse(url).netloc.replace("www.", "")
    for known_domain, scraper_class in SCRAPER_URL_MAP.items():
        if known_domain in domain:
            return scraper_class()
    raise ValueError(f"No scraper registered for URL: {url}")
