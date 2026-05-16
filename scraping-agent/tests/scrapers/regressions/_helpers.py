class RecordingPageLoader:
    def __init__(self, html_by_url=None, default_html=""):
        self.html_by_url = html_by_url or {}
        self.default_html = default_html
        self.requested_urls = []

    def load_content(self, page_url):
        self.requested_urls.append(page_url)
        return self.html_by_url.get(page_url, self.default_html)

    def close(self):
        return None
