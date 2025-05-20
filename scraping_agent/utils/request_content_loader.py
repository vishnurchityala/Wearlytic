from abc import ABC, abstractmethod
from base_content_loader import BaseContentLoader
import requests

class RequestContentLoader(BaseContentLoader):
    def __init__(self, headers=None):
        """
        Initializes the Request-based content loader with optional HTTP headers.

        Args:
            headers (dict): HTTP headers to use for the request.
        """
        super().__init__(headers)

    def load_content(self, page_url):
        """
        Sends a GET request to the specified URL and returns the raw HTML content.

        Args:
            page_url (str): The URL of the page to retrieve.

        Returns:
            str: The raw HTML content of the page.
        """
        response = requests.get(page_url,headers=self.headers)
        response.raise_for_status()
        return response.text

if __name__ == "__main__":
    demo_page_url = "https://example.com/"
    print("* Creating Page Content Loader using Requests.")
    content_loader = RequestContentLoader()
    print("* Using Page Content Loader using Requests.")
    page_content = content_loader.load_content(page_url=demo_page_url)
    print("* Page Content Loaded:")
    print(page_content[-1000:-1])