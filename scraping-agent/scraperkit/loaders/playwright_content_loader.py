import os

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from scraperkit.exceptions import BadURLException, ContentNotLoadedException, TimeoutException as ScraperTimeoutException
from scraperkit.base import BaseContentLoader

class PlaywrightContentLoader(BaseContentLoader):
    def __init__(self, headers=None, timeout=10000,headless=True):
        self.headers = headers or {}
        self.timeout = timeout
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self._init_browser()

    def _init_browser(self):
        self.playwright = sync_playwright().start()
        executable_path = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
        launch_options = {"headless": self.headless}
        if executable_path:
            launch_options["executable_path"] = executable_path
        self.browser = self.playwright.chromium.launch(**launch_options)
        context = self.browser.new_context(
            user_agent=self.headers.get("User-Agent"),
            locale=self.headers.get("Accept-Language"),
        )
        self.page = context.new_page()

    def load_content(self, page_url):
        try:
            self.page.set_default_navigation_timeout(self.timeout)

            self.page.goto(page_url, wait_until="load")
            content = self.page.content()
            return content

        except PlaywrightTimeoutError:
            raise ScraperTimeoutException(f"Timeout while loading page: {page_url}")
        except ValueError:
            raise BadURLException(f"Invalid URL provided: {page_url}")
        except PlaywrightError as e:
            raise ContentNotLoadedException(f"Playwright error while loading page {page_url}: {str(e)}")
        except Exception as e:
            raise ContentNotLoadedException(f"Unexpected error while loading page {page_url}: {str(e)}")

    def close(self):
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def __del__(self):
        self.close()
