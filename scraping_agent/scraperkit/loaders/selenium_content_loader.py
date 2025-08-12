import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException as SeleniumTimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from scraperkit.base.base_content_loader import BaseContentLoader
from scraperkit.exceptions import BadURLException, TimeoutException, DriverNotInitializedException
from scraperkit.utils import get_driver_path

class SeleniumContentLoader(BaseContentLoader):
    def __init__(self, headers=None, timeout=30,headless=True):
        super().__init__()
        self.timeout = timeout
        self.headless = headless
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
        self.service = None
        self.driver = None
        try:
            self._init_driver()
        except Exception as e:
            raise DriverNotInitializedException()

    def _init_driver(self):
        chrome_options = Options()

        for key, value in self.headers.items():
            chrome_options.add_argument(f"--{key.lower()}={value}")

        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--start-maximized")
        
        chrome_options.page_load_strategy = 'eager'

        self.service = Service(get_driver_path())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})"
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})"
        )

    def load_content(self, page_url):
        try:
            self.driver.get(page_url)
            
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(5)
            
            page_source = self.driver.page_source

            soup = BeautifulSoup(page_source, "html.parser")
            pre_tag = soup.find("pre", style=lambda s: s and "pre-wrap" in s)
            if pre_tag and "not found" in pre_tag.get_text(strip=True).lower():
                raise BadURLException(f"Page not found (404) at URL: {page_url}")

            return page_source

        except SeleniumTimeoutException as e:
            raise TimeoutException(f"Timeout while loading page: {page_url}. Error: {str(e)}")

        except WebDriverException as e:
            raise BadURLException(f"Bad URL or navigation error: {page_url}. Error: {str(e)}")

        except Exception as e:
            raise e

    def close(self):
        if self.driver:
            self.driver.quit()
        if self.service:
            self.service.stop()


if __name__ == "__main__":
    demo_page_url = "https://bluorng.com/collections/polos"
    print("* Creating Page Content Loader using Selenium.")
    content_loader = SeleniumContentLoader()
    print("* Using Page Content Loader using Selenium.")
    page_content = content_loader.load_content(page_url=demo_page_url)
    print("* Page Content Loaded:")
    print(page_content[-1000:-1])
    content_loader.close()
