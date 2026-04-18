from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

import api.routes.status as status_route


class FakeJobsManager:
    def __init__(self, *, job=None, exc=None):
        self.job = job
        self.exc = exc

    def get_job(self, job_id):
        if self.exc:
            raise self.exc
        return self.job


class FakeJobResultsManager:
    def __init__(self, *, result=None, exc=None):
        self.result = result
        self.exc = exc

    def get_result(self, job_id):
        if self.exc:
            raise self.exc
        return self.result


@pytest.mark.unit
def test_get_listing_status_returns_job_when_present(monkeypatch):
    monkeypatch.setattr(
        status_route,
        "job_manager",
        FakeJobsManager(
            job={
                "job_id": "job-123",
                "webpage_url": "https://example.com/product/1",
                "priority": "high",
                "type_page": "product",
                "status": "completed",
                "created_at": datetime(2026, 4, 18, tzinfo=timezone.utc).isoformat(),
                "completed_at": None,
                "error_message": None,
            },
        ),
    )

    response = status_route.get_listing_status("job-123")

    assert response["job_id"] == "job-123"


@pytest.mark.unit
def test_get_listing_status_returns_404_when_job_missing(monkeypatch):
    monkeypatch.setattr(status_route, "job_manager", FakeJobsManager(job=None))

    with pytest.raises(HTTPException) as exc_info:
        status_route.get_listing_status("job-404")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Job job-404 not found"


@pytest.mark.unit
def test_get_listing_status_returns_503_when_backend_fails(monkeypatch):
    monkeypatch.setattr(
        status_route,
        "job_manager",
        FakeJobsManager(exc=RuntimeError("mongo unavailable")),
    )

    with pytest.raises(HTTPException) as exc_info:
        status_route.get_listing_status("job-500")

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Failed to fetch job status"


@pytest.mark.unit
def test_get_listing_result_returns_result_when_present(monkeypatch):
    monkeypatch.setattr(
        status_route,
        "job_result_manager",
        FakeJobResultsManager(
            result={
                "job_id": "job-200",
                "result": {
                    "items": [
                        {
                            "url": "https://example.com/product/1",
                            "page_rank": 1.0,
                        }
                    ]
                },
                "status": "completed",
                "completed_at": datetime(2026, 4, 18, tzinfo=timezone.utc).isoformat(),
                "error_message": None,
            },
        ),
    )

    response = status_route.get_listing_result("job-200")

    assert response["job_id"] == "job-200"
    assert response["result"]["items"][0]["page_rank"] == 1.0


@pytest.mark.unit
def test_get_listing_result_returns_404_when_result_missing(monkeypatch):
    monkeypatch.setattr(status_route, "job_result_manager", FakeJobResultsManager(result=None))

    with pytest.raises(HTTPException) as exc_info:
        status_route.get_listing_result("job-404")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Job job-404 not found"


@pytest.mark.unit
def test_get_listing_result_returns_503_when_backend_fails(monkeypatch):
    monkeypatch.setattr(
        status_route,
        "job_result_manager",
        FakeJobResultsManager(exc=RuntimeError("mongo unavailable")),
    )

    with pytest.raises(HTTPException) as exc_info:
        status_route.get_listing_result("job-503")

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Failed to fetch job result"
