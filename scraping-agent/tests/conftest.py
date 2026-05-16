import os
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--scraper-log-dir",
        action="store",
        default=os.environ.get("SCRAPERKIT_TEST_LOG_DIR"),
        help="Directory where scraper integration test artifacts should be written.",
    )


@pytest.fixture(scope="session")
def scraper_test_artifact_root(pytestconfig):
    configured_dir = pytestconfig.getoption("--scraper-log-dir")
    if configured_dir:
        artifact_root = Path(configured_dir)
    else:
        artifact_root = Path(__file__).resolve().parent / "artifacts" / "scraper_runs"

    artifact_root.mkdir(parents=True, exist_ok=True)
    return artifact_root
