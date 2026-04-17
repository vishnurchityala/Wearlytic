from types import SimpleNamespace

import pytest

import api.celery_worker as celery_worker
from api.models import Listing


class FakeJobsManager:
    def __init__(self):
        self.updates = []

    def update_job(self, job_id, updates):
        self.updates.append((job_id, updates))
        return SimpleNamespace(matched_count=1)


class FakeJobResultsManager:
    def __init__(self):
        self.results = []

    def create_result(self, result):
        self.results.append(result)


class FakeCache:
    def __init__(self):
        self.inserted = []

    def insert(self, source_website, scraper_object):
        self.inserted.append((source_website, scraper_object))


class DummyProductDetails:
    def model_dump(self, mode="json"):
        return {
            "id": "dummy_1",
            "title": "Dummy Product",
            "price": 10.0,
            "category": "T-Shirts",
            "gender": None,
            "url": "https://example.com/product/1",
            "image_url": "https://example.com/image.jpg",
            "colors": None,
            "sizes": ["M"],
            "material": None,
            "description": "A test product",
            "rating": None,
            "review_count": None,
            "processed": False,
            "scraped_datetime": None,
            "processed_datetime": None,
            "page_index": 0,
            "page_content": "<html></html>",
        }


class DummyScraper:
    def __init__(self, product_exc=None, listing_exc=None):
        self.product_exc = product_exc
        self.listing_exc = listing_exc
        self.close_calls = 0

    def get_product_details(self, product_page_url):
        if self.product_exc:
            raise self.product_exc
        return DummyProductDetails()

    def get_pagination_details(self, page_url):
        if self.listing_exc:
            raise self.listing_exc
        return {
            "current_page": 1,
            "total_pages": 1,
            "next_page_url": None,
        }

    def get_product_listings(self, listings_page_url, page=1):
        if self.listing_exc:
            raise self.listing_exc
        return ["https://example.com/product/1"]

    def close(self):
        self.close_calls += 1


@pytest.mark.unit
def test_run_product_job_persists_failed_result_and_closes_scraper(monkeypatch):
    job_manager = FakeJobsManager()
    job_result_manager = FakeJobResultsManager()
    cache = FakeCache()
    scraper = DummyScraper(product_exc=RuntimeError("boom"))

    monkeypatch.setattr(celery_worker, "get_scraper_from_url", lambda url: scraper)
    monkeypatch.setattr(celery_worker, "extract_domain", lambda url: "dummyshop")
    monkeypatch.setattr(celery_worker, "ScraperCache", cache)

    message = celery_worker._run_product_job(
        job_id="job-1",
        url="https://dummyshop.com/product/1",
        job_manager=job_manager,
        job_result_manager=job_result_manager,
    )

    assert message == "Scrape Product Task failed : https://dummyshop.com/product/1"
    assert job_manager.updates[0][1] == {"status": "processing", "error_message": None}
    assert job_manager.updates[-1][1]["status"] == "failed"
    assert job_manager.updates[-1][1]["error_message"] == "boom"
    assert len(job_result_manager.results) == 1
    assert job_result_manager.results[0].status == "failed"
    assert job_result_manager.results[0].result == []
    assert job_result_manager.results[0].error_message == "boom"
    assert scraper.close_calls == 1
    assert cache.inserted == []


@pytest.mark.unit
def test_run_listing_job_closes_scraper_on_failure(monkeypatch):
    job_manager = FakeJobsManager()
    job_result_manager = FakeJobResultsManager()
    cache = FakeCache()
    scraper = DummyScraper(listing_exc=RuntimeError("listing exploded"))

    monkeypatch.setattr(celery_worker, "get_scraper_from_url", lambda url: scraper)
    monkeypatch.setattr(celery_worker, "extract_domain", lambda url: "dummyshop")
    monkeypatch.setattr(celery_worker, "ScraperCache", cache)

    message = celery_worker._run_listing_job(
        job_id="job-2",
        url="https://dummyshop.com/listing",
        job_manager=job_manager,
        job_result_manager=job_result_manager,
    )

    assert message == "Scrape Listing Task failed : https://dummyshop.com/listing"
    assert job_manager.updates[-1][1]["status"] == "failed"
    assert job_result_manager.results[0].status == "failed"
    assert isinstance(job_result_manager.results[0].result, Listing)
    assert job_result_manager.results[0].result.items == []
    assert scraper.close_calls == 1
    assert cache.inserted == []


@pytest.mark.unit
def test_run_product_job_reinserts_scraper_into_cache_on_success(monkeypatch):
    job_manager = FakeJobsManager()
    job_result_manager = FakeJobResultsManager()
    cache = FakeCache()
    scraper = DummyScraper()

    monkeypatch.setattr(celery_worker, "get_scraper_from_url", lambda url: scraper)
    monkeypatch.setattr(celery_worker, "extract_domain", lambda url: "dummyshop")
    monkeypatch.setattr(celery_worker, "ScraperCache", cache)

    message = celery_worker._run_product_job(
        job_id="job-3",
        url="https://dummyshop.com/product/1",
        job_manager=job_manager,
        job_result_manager=job_result_manager,
    )

    assert message == "Scrape Product Task completed : https://dummyshop.com/product/1"
    assert job_manager.updates[-1][1]["status"] == "completed"
    assert job_result_manager.results[0].status == "completed"
    assert scraper.close_calls == 0
    assert cache.inserted == [("dummyshop", scraper)]
