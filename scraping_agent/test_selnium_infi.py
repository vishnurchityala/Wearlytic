import json
from datetime import datetime
from pydantic import BaseModel
from scraperkit.scrapers import JayWalkingScraper

# Initialize scraper
scraper = JayWalkingScraper()

listings_url = "https://www.jaywalking.in/collections/tiedye"

# Fetch pagination details
pagination = scraper.get_pagination_details(listings_url)
print("\n✅ Pagination Details:")
print(json.dumps(pagination, indent=2))

total_pages = pagination.get("total_pages", 1)

all_product_urls = []

# Loop through all pages
for page in range(1, total_pages + 1):
    # If multi-page, adjust the URL (depends on site’s pagination pattern)
    page_url = listings_url
    if page > 1:
        page_url = f"{listings_url}?page={page}"
    
    print(f"\n🔎 Fetching product links from page {page}: {page_url}")
    product_links = scraper.get_product_listings(page_url)
    all_product_urls.extend(product_links)

print(f"\n✅ Total products found: {len(all_product_urls)}")

# Loop through all products
for idx, product_url in enumerate(all_product_urls, start=1):
    print(f"\n====== Product {idx} ======")
    print(f"Fetching details for: {product_url}")
    
    try:
        product = scraper.get_product_details(product_url)
        
        # Print each field nicely
        for field_name, value in product.dict().items():
            if isinstance(value, datetime):
                value = value.isoformat()
            print(f"{field_name}: {value}")
    
    except Exception as e:
        print(f"❌ Failed to scrape {product_url}: {e}")