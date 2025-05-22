import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from base_content_loader import BaseContentLoader

class SeleniumContentLoader(BaseContentLoader):
    def __init__(self, headers=None, timeout=10):
        super().__init__()
        self.timeout = timeout
        self.service = None
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        chrome_options = Options()

        if 'User-Agent' in self.headers:
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
        if 'Accept-Language' in self.headers:
            chrome_options.add_argument(f"accept-language={self.headers['Accept-Language']}")

        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def load_content(self, page_url):
        self.driver.get(page_url)
        time.sleep(self.timeout)
        return self.driver.page_source

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