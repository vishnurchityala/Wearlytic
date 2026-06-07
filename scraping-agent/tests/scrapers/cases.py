from dataclasses import dataclass

from scraperkit import SCRAPER_URL_MAP
from scraperkit.base.base_scraper import BaseScraper


@dataclass(frozen=True)
class ScraperCase:
    source_name: str
    scraper_cls: type[BaseScraper]
    listing_url: str


SCRAPER_TEST_CASES = (
    ScraperCase(
        source_name="amazon",
        scraper_cls=SCRAPER_URL_MAP["amazon"],
        listing_url="https://www.amazon.in/s?k=men+t-shirts",
    ),
    ScraperCase(
        source_name="myntra",
        scraper_cls=SCRAPER_URL_MAP["myntra"],
        listing_url="https://www.myntra.com/mens-tshirts",
    ),
    ScraperCase(
        source_name="bluorng",
        scraper_cls=SCRAPER_URL_MAP["bluorng"],
        listing_url="https://bluorng.com/collections/t-shirts",
    ),
    ScraperCase(
        source_name="jaywalking",
        scraper_cls=SCRAPER_URL_MAP["jaywalking"],
        listing_url="https://www.jaywalking.in/collections/t-shirt",
    ),
    ScraperCase(
        source_name="thesouledstore",
        scraper_cls=SCRAPER_URL_MAP["thesouledstore"],
        listing_url="https://www.thesouledstore.com/men-classic-tshirts",
    ),
)
