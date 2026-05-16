import pytest

from scraperkit.exceptions import BadURLException, ContentNotLoadedException, TimeoutException
from scraperkit.loaders.request_content_loader import RequestContentLoader


LIVE_HTML_URL = "https://example.com/"
SLOW_RESPONSE_URL = "https://httpbin.org/delay/5"
HTTP_ERROR_URL = "https://httpbin.org/status/500"


@pytest.mark.integration
def test_request_content_loader_returns_real_response_text():
    loader = RequestContentLoader()

    page_content = loader.load_content(LIVE_HTML_URL)

    assert "<html" in page_content.lower()
    assert "example domain" in page_content.lower()


@pytest.mark.integration
def test_request_content_loader_wraps_invalid_urls():
    with pytest.raises(BadURLException):
        RequestContentLoader().load_content("notaurl")


@pytest.mark.integration
def test_request_content_loader_wraps_timeouts_against_real_website():
    with pytest.raises(TimeoutException):
        RequestContentLoader(timeout=0.001).load_content(SLOW_RESPONSE_URL)


@pytest.mark.integration
def test_request_content_loader_wraps_http_errors_against_real_website():
    with pytest.raises(ContentNotLoadedException):
        RequestContentLoader().load_content(HTTP_ERROR_URL)
