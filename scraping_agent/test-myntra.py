from scraperkit.scrapers import MyntraScraper

if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    print("Initializing Myntra Scraper...")
    scraper = MyntraScraper(headers=headers)

    try:
        search_url = "https://www.myntra.com/tshirts"
        print(f"\nTesting search URL: {search_url}")

        print("\n1. Testing page content retrieval...")
        html_content = scraper.get_page_content(search_url)
        if html_content:
            print(f"✓ Successfully retrieved {len(html_content)} characters of HTML")
        else:
            print("✗ Failed to retrieve content")
            exit(1)

        print("\n2. Testing pagination details...")
        pagination_details = scraper.get_pagination_details(search_url)
        print("Pagination Details:")
        for key, value in pagination_details.items():
            print(f"  {key}: {value}")

        print("\n3. Testing product listings...")
        product_links = scraper.get_product_listings(search_url)
        print(f"Found {len(product_links)} products on first page")
        
        if product_links:
            print("\nSample Product Links:")
            for i, link in enumerate(product_links[:10], 1):
                print(f"  {i}. {link}")

            print("\n4. Testing product details extraction...")
            for test_product_url in product_links[:10]:
                print(f"Testing with product: {test_product_url}")
                
                product_details = scraper.get_product_details(test_product_url)
                if product_details:
                    print("\nProduct Details:")
                    for key, value in product_details.__dict__.items():
                        if not key.startswith('_'):
                            print(f"  {key}: {value}")
                else:
                    print("✗ Failed to extract product details")

    except Exception as e:
        print(f"\nError during testing: {e}")
    finally:
        print("\nCleaning up resources...")
        scraper.close()
        print("Done!")
