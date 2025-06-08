from scraperkit.base import BaseContentLoader
from scraperkit.exceptions import BadURLException, ContentNotLoadedException, TimeoutException
import requests

class RequestContentLoader(BaseContentLoader):
    def __init__(self, headers=None, timeout=10):
        super().__init__(headers, timeout)

    def load_content(self, page_url):
        try:
            response = requests.get(page_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except (requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError,
                requests.exceptions.MissingSchema) as e:
            raise BadURLException(f"Bad URL provided or server not reachable: {page_url}. Error: {str(e)}")

        except requests.exceptions.Timeout as e:
            raise TimeoutException(f"Timeout while loading page: {page_url}. Error: {str(e)}")

        except requests.exceptions.HTTPError as e:
            raise ContentNotLoadedException(f"HTTP error {response.status_code} while loading page: {page_url}. Error: {str(e)}")

        except Exception as e:
            raise ContentNotLoadedException(f"Unexpected error while loading page: {page_url}. Error: {str(e)}")


if __name__ == "__main__":
    demo_page_url = "https://example.com/"
    print("* Creating Page Content Loader using Requests.")
    content_loader = RequestContentLoader()
    print("* Using Page Content Loader using Requests.")
    page_content = content_loader.load_content(page_url=demo_page_url)
    print("* Page Content Loaded:")
    print(page_content[-1000:-1])