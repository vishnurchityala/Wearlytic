from scraperkit.base.base_content_loader  import BaseContentLoader
import requests

class RequestContentLoader(BaseContentLoader):
    def __init__(self, headers=None):
        super().__init__(headers)

    def load_content(self, page_url):
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