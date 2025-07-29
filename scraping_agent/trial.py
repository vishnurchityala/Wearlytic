from scraperkit.scrapers import AmazonScraper

scraper = AmazonScraper()
print(scraper.get_product_details("https://www.amazon.in/RAMRAJ-Cotton-Sleeve-Matching-Readymade/dp/B0DK51G763/"))