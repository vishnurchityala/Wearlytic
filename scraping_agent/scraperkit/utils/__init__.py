import os
from dotenv import load_dotenv
from urllib.parse import urlparse

def get_scraper_from_url(url: str):
    from scraperkit import SCRAPER_URL_MAP
    domain = urlparse(url).netloc.replace("www.", "")
    for known_domain, scraper_class in SCRAPER_URL_MAP.items():
        if known_domain in domain:
            return scraper_class()
    raise ValueError(f"No scraper registered for URL: {url}")

def get_driver_path():
    load_dotenv()
    platform = os.getenv("PLATFORM")
    if platform == 'macosarm64':
        return "./scraperkit/drivers/chromedriver-mac-arm64/chromedriver"
    elif platform == 'macosamd64':
        return "./scraperkit/drivers/chromedriver-mac-x64/chromedriver"
    elif platform == 'win64':
        return "./scraperkit/drivers/chromedriver-win64/chromedriver.exe"
