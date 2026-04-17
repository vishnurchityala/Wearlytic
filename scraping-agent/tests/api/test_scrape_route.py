from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import api.routes.scrape as scrape_route
from api.models import JobRequest


class FakeJobsManager:
    def __init__(self, call_order):
        self.call_order = call_order
        self.created_jobs = []
        self.deleted_job_ids = []

    def create_job(self, job):
        self.call_order.append("create_job")
        self.created_jobs.append(job)

    def delete_job(self, job_id):
        self.call_order.append("delete_job")
        self.deleted_job_ids.append(job_id)


class FakeTask:
    def __init__(self, call_order, job_manager, should_fail=False):
        self.call_order = call_order
        self.job_manager = job_manager
        self.should_fail = should_fail

    def apply_async(self, args, queue, task_id):
        self.call_order.append("apply_async")
        assert self.job_manager.created_jobs, "job must be created before publishing"
        assert self.job_manager.created_jobs[0].job_id == task_id
        if self.should_fail:
            raise RuntimeError("broker unavailable")
        return SimpleNamespace(id=task_id)


@pytest.mark.unit
def test_start_scrape_creates_job_before_enqueuing(monkeypatch):
    call_order = []
    fake_job_manager = FakeJobsManager(call_order)
    fake_task = FakeTask(call_order, fake_job_manager)

    monkeypatch.setattr(scrape_route, "job_manager", fake_job_manager)
    monkeypatch.setattr(scrape_route, "scrape_product_task", fake_task)
    monkeypatch.setattr(scrape_route, "uuid4", lambda: "job-123")

    response = scrape_route.start_scrape(
        JobRequest(
            webpage_url="https://example.com/product/1",
            priority="high",
            type_page="product",
        )
    )

    assert call_order == ["create_job", "apply_async"]
    assert response == {"job_id": "job-123"}


@pytest.mark.unit
def test_start_scrape_cleans_up_job_record_when_enqueue_fails(monkeypatch):
    call_order = []
    fake_job_manager = FakeJobsManager(call_order)
    fake_task = FakeTask(call_order, fake_job_manager, should_fail=True)

    monkeypatch.setattr(scrape_route, "job_manager", fake_job_manager)
    monkeypatch.setattr(scrape_route, "scrape_listing_task", fake_task)
    monkeypatch.setattr(scrape_route, "uuid4", lambda: "job-456")

    with pytest.raises(HTTPException) as exc_info:
        scrape_route.start_scrape(
            JobRequest(
                webpage_url="https://example.com/listing",
                priority="low",
                type_page="listing",
            )
        )

    assert exc_info.value.status_code == 503
    assert call_order == ["create_job", "apply_async", "delete_job"]
    assert fake_job_manager.deleted_job_ids == ["job-456"]
