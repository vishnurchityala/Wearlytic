import json

import pytest

from tests.scrapers.scrape_artifact_logger import ScrapeArtifactLogger


class DummyScraper:
    def get_page_content(self, page_url):
        return f"<html><body>{page_url}</body></html>"


class FailingScraper:
    def get_page_content(self, page_url):
        raise RuntimeError(f"boom: {page_url}")


class DummyProduct:
    def __init__(self, url, page_content):
        self.url = url
        self.page_content = page_content

    def model_dump(self, mode="json"):
        return {
            "id": "dummy_1",
            "title": "Dummy Product",
            "price": 10.0,
            "description": "A test product",
            "url": self.url,
            "image_url": "https://example.com/image.jpg",
            "page_content": self.page_content,
        }


@pytest.mark.unit
def test_scrape_artifact_logger_writes_html_and_summary(tmp_path):
    logger = ScrapeArtifactLogger(
        artifact_root=tmp_path,
        source_name="example",
        scraper_name="DummyScraper",
        test_nodeid="tests/scrapers/test_dummy.py::test_dummy",
        listing_url="https://example.com/listing",
    )
    scraper = DummyScraper()

    logger.attach_to_scraper(scraper)
    listing_html = scraper.get_page_content("https://example.com/listing")
    product_html = scraper.get_page_content("https://example.com/product/1")

    logger.record_pagination(
        {
            "current_page": "https://example.com/listing",
            "total_pages": 1,
            "next_page_url": None,
        }
    )
    logger.record_listings(["https://example.com/product/1"])
    logger.record_product(
        DummyProduct(url="https://example.com/product/1", page_content=product_html)
    )
    logger.finalize(status="completed")

    summary = json.loads(logger.summary_path.read_text(encoding="utf-8"))

    assert listing_html
    assert summary["status"] == "completed"
    assert len(summary["page_fetches"]) == 2
    assert summary["page_fetches"][0]["status"] == "loaded"
    assert summary["page_fetches"][0]["html_file"].endswith(".html")
    assert summary["extracted_data"]["listings"]["count"] == 1
    assert (
        summary["extracted_data"]["product"]["page_content_html_file"]
        == summary["page_fetches"][1]["html_file"]
    )


@pytest.mark.unit
def test_scrape_artifact_logger_records_fetch_errors(tmp_path):
    logger = ScrapeArtifactLogger(
        artifact_root=tmp_path,
        source_name="example",
        scraper_name="FailingScraper",
        test_nodeid="tests/scrapers/test_dummy.py::test_dummy_failure",
        listing_url="https://example.com/listing",
    )
    scraper = FailingScraper()

    logger.attach_to_scraper(scraper)

    with pytest.raises(RuntimeError):
        scraper.get_page_content("https://example.com/listing")

    logger.finalize(status="failed")
    summary = json.loads(logger.summary_path.read_text(encoding="utf-8"))

    assert summary["status"] == "failed"
    assert len(summary["page_fetches"]) == 1
    assert summary["page_fetches"][0]["status"] == "failed"
    assert summary["page_fetches"][0]["html_file"] is None
