import logging

from fastapi import APIRouter, HTTPException, Depends, status
from api.models import JobResult
from api.db import JobsManager, JobResultsManager
from api.security import verify_token


router = APIRouter(prefix="/api/scrapingagent/scrape",redirect_slashes=False)
job_manager = JobsManager()
job_result_manager = JobResultsManager()
logger = logging.getLogger(__name__)


def _load_record_or_raise(task_id: str, loader, not_found_detail: str, backend_failure_detail: str):
    try:
        record = loader(task_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch record for job %s", task_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=backend_failure_detail,
        ) from exc

    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)

    return record

@router.get("/{task_id}/status/", dependencies=[Depends(verify_token)])
def get_listing_status(task_id: str):
    return _load_record_or_raise(
        task_id=task_id,
        loader=job_manager.get_job,
        not_found_detail=f"Job {task_id} not found",
        backend_failure_detail="Failed to fetch job status",
    )


@router.get("/{task_id}/result/", dependencies=[Depends(verify_token)])
def get_listing_result(task_id: str) -> JobResult:
    return _load_record_or_raise(
        task_id=task_id,
        loader=job_result_manager.get_result,
        not_found_detail=f"Job {task_id} not found",
        backend_failure_detail="Failed to fetch job result",
    )
