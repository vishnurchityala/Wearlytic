from scraperkit.base.base_content_loader  import BaseContentLoader
from playwright.sync_api import sync_playwright
import time
import random
import logging
logging.basicConfig(level=logging.ERROR)

class PlaywrightContentLoader(BaseContentLoader):
    """
    Playwright implementation with improved timeout handling and anti-bot detection.
    """
    
    def __init__(self, headers=None, headless=True, wait_time=30, browser_type="chromium"):
        super().__init__(headers)
        self.headless = headless
        self.wait_time = wait_time
        self.browser_type = browser_type
        
    def load_content(self, page_url):
        """
        Loads content using Playwright with multiple wait strategies.
        """
        try:
            with sync_playwright() as p:
                browser_engine = getattr(p, self.browser_type)
                browser = browser_engine.launch(
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ] if self.browser_type == "chromium" else []
                )
                
                context = browser.new_context(
                    user_agent=self.headers.get("User-Agent"),
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers=self.headers,
                    ignore_https_errors=True
                )
                
                page = context.new_page()
                page.set_default_timeout(self.wait_time * 1000)
                page.set_default_navigation_timeout(self.wait_time * 1000)
                
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    window.chrome = {
                        runtime: {},
                    };
                    
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({ state: 'granted' }),
                        }),
                    });
                    
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                """)
                
                try:
                    page.goto(page_url, wait_until='networkidle', timeout=self.wait_time * 1000)
                except Exception as e:
                    logging.warning(f"Networkidle failed: {e}, trying domcontentloaded")
                    try:
                        page.goto(page_url, wait_until='domcontentloaded', timeout=self.wait_time * 1000)
                        page.wait_for_timeout(3000)
                    except Exception as e2:
                        logging.warning(f"Domcontentloaded failed: {e2}, trying load event")
                        page.goto(page_url, wait_until='load', timeout=self.wait_time * 1000)
                        page.wait_for_timeout(5000)
                
                try:
                    page.wait_for_selector('body', timeout=5000)
                except:
                    logging.warning("Body selector not found, continuing anyway")
                
                time.sleep(random.uniform(1, 2))
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 4)")
                time.sleep(random.uniform(0.5, 1))
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(random.uniform(0.5, 1))
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1, 2))
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(random.uniform(0.5, 1))
                
                content = page.content()
                browser.close()
                
                return content
                
        except Exception as e:
            logging.error(f"Error loading content from {page_url}: {e}")
            return None


if __name__ == "__main__":
    demo_page_url = "https://bluorng.com/collections/polos"
    print("* Creating Page Content Loader using Playwright.")
    content_loader = PlaywrightContentLoader()
    print("* Using Page Content Loader using Playwright.")
    page_content = content_loader.load_content(page_url=demo_page_url)
    print(f"* Page Content Loaded with Lenght: {len(page_content)}")