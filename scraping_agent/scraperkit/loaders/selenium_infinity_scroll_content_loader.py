import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException as SeleniumTimeoutException,
    InvalidArgumentException,
    NoSuchElementException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scraperkit.base.base_content_loader import BaseContentLoader
from scraperkit.exceptions import BadURLException, ContentNotLoadedException, TimeoutException


class SeleniumInfinityScrollContentLoader(BaseContentLoader):

    def __init__(self, headers=None, max_scrolls=None, headless=True, target_class_name=None, scroll_delay=3):
        super().__init__()
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.max_scrolls = max_scrolls or 30
        self.last_height = 0
        self.new_height = 0
        self.scroll_delay = scroll_delay
        self.headless = headless
        self.target_class_name = target_class_name
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

        if self.headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def load_content(self, page_url):
        try:
            self.driver.get(page_url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0

            for i in range(0, self.max_scrolls):
                try:
                    target_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, self.target_class_name))
                    )

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                        target_element
                    )

                except (NoSuchElementException, SeleniumTimeoutException):
                    current_position = self.driver.execute_script("return window.pageYOffset;")
                    self.driver.execute_script(f"window.scrollTo(0, {current_position + 800});")

                time.sleep(self.scroll_delay)

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_count += 1

                if new_height == last_height:
                    break

                last_height = new_height

            return self.driver.page_source

        except SeleniumTimeoutException as e:
            raise TimeoutException(f"Timeout while loading or scrolling page: {page_url}. Error: {str(e)}")

        except InvalidArgumentException as e:
            raise BadURLException(f"Invalid URL provided: {page_url}. Error: {str(e)}")

        except WebDriverException as e:
            raise ContentNotLoadedException(f"WebDriver error while loading page: {page_url}. Error: {str(e)}")

        except Exception as e:
            raise ContentNotLoadedException(f"Unexpected error while loading page: {page_url}. Error: {str(e)}")

    def close(self):
        if self.driver:
            self.driver.quit()
        if self.service:
            self.service.stop()


if __name__ == "__main__":
    loader = SeleniumInfinityScrollContentLoader(
        target_class_name="footerlinks",
        scroll_delay=5,
        headless=False,
        max_scrolls=30
    )
    try:
        content = loader.load_content("https://www.thesouledstore.com/men/t-shirts")
        print(f"Loaded content length: {len(content)} characters")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        loader.close()
