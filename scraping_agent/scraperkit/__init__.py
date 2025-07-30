from scraperkit.scrapers import AmazonScraper
from scraperkit.scrapers import MyntraScraper
from scraperkit.scrapers import BluOrngScraper
from scraperkit.scrapers import JayWalkingScraper
from scraperkit.scrapers import SouledStoreScraper

SCRAPER_URL_MAP = {
    "amazon.in": AmazonScraper,
    "myntra.com": MyntraScraper,
    "bluorng.com": BluOrngScraper,
    "jaywalking.in": JayWalkingScraper,
    "thesouledstore.com": SouledStoreScraper
}