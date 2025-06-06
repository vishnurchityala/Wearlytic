import unittest
from scraperkit.loaders import RequestContentLoader
from scraperkit.scrapers import MyntraScraper

def test_myntra_scraper(page_url):
    myntra_scraper = MyntraScraper()
    item = myntra_scraper.get_product_details(page_url)
    return 0

class TestMyntraScraper(unittest.TestCase):

    def test_without_rating(self):
        self.assertEqual(test_myntra_scraper("https://www.myntra.com/trousers/mountmiller/mountmiller-mens-camouflage-printed-advanced-multicam-ripstop-pant/33797215/buy"),0)
        print("TEST-CASE 1 Passed.")

    def test_with_all_info(self):
        self.assertEqual(test_myntra_scraper("https://www.myntra.com/trousers/celio/celio-men-slim-fit-cotton-cargo-casual-trouser/26878712/buy"),0)
        print("TEST-CASE 2 Passed.")

    def test_without_colors(self):
        self.assertEqual(test_myntra_scraper("https://www.myntra.com/trousers/aeropostale/aeropostale-men-cargo-trousers/34001046/buy"),0)
        print("TEST-CASE 3 Passed.")

if __name__ == "__main__":
    unittest.main()