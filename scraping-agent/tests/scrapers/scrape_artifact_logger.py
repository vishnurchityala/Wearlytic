import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_isoformat() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return slug or "artifact"


def _json_ready(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_ready(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


class ScrapeArtifactLogger:
    def __init__(
        self,
        artifact_root: Path,
        source_name: str,
        scraper_name: str,
        test_nodeid: str,
        listing_url: str,
    ):
        self._fetch_counter = 0
        self._run_dir = (
            artifact_root
            / f"{_utc_timestamp()}_{_slugify(source_name)}"
        )
        self._html_dir = self._run_dir / "html"
        self._html_dir.mkdir(parents=True, exist_ok=True)
        self.summary_path = self._run_dir / "summary.json"

        self.summary = {
            "test_nodeid": test_nodeid,
            "source_name": source_name,
            "scraper_name": scraper_name,
            "listing_url": listing_url,
            "status": "running",
            "started_at": _utc_isoformat(),
            "finished_at": None,
            "run_directory": str(self._run_dir.resolve()),
            "page_fetches": [],
            "extracted_data": {
                "pagination": None,
                "listings": None,
                "product": None,
            },
            "errors": [],
        }
        self.flush()

    @property
    def run_dir(self) -> Path:
        return self._run_dir

    def attach_to_scraper(self, scraper) -> None:
        original_get_page_content = scraper.get_page_content

        def logged_get_page_content(page_url):
            try:
                page_content = original_get_page_content(page_url)
                html_file = self._write_html_snapshot(page_url, page_content)
                self.summary["page_fetches"].append(
                    {
                        "url": page_url,
                        "status": "loaded",
                        "fetched_at": _utc_isoformat(),
                        "html_file": str(html_file.resolve()),
                        "content_length": len(page_content or ""),
                    }
                )
                self.flush()
                return page_content
            except Exception as exc:
                self.summary["page_fetches"].append(
                    {
                        "url": page_url,
                        "status": "failed",
                        "fetched_at": _utc_isoformat(),
                        "html_file": None,
                        "content_length": 0,
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                )
                self.flush()
                raise

        scraper.get_page_content = logged_get_page_content

    def record_pagination(self, pagination: dict) -> None:
        self.summary["extracted_data"]["pagination"] = _json_ready(pagination)
        self.flush()

    def record_listings(self, listings: list[str]) -> None:
        self.summary["extracted_data"]["listings"] = {
            "count": len(listings),
            "items": _json_ready(listings),
        }
        self.flush()

    def record_product(self, product) -> None:
        product_payload = _json_ready(product)
        product_payload["page_content_html_file"] = self._latest_html_file_for_url(
            str(product.url)
        )
        self.summary["extracted_data"]["product"] = product_payload
        self.flush()

    def record_error(self, stage: str, exc: Exception) -> None:
        self.summary["errors"].append(
            {
                "stage": stage,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "recorded_at": _utc_isoformat(),
            }
        )
        self.flush()

    def finalize(self, status: str) -> None:
        self.summary["status"] = status
        self.summary["finished_at"] = _utc_isoformat()
        self.flush()

    def flush(self) -> None:
        self.summary_path.write_text(
            json.dumps(self.summary, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _write_html_snapshot(self, page_url: str, page_content: str | None) -> Path:
        self._fetch_counter += 1
        parsed = urlparse(page_url)
        path_part = parsed.path.strip("/") or "root"
        query_part = f"_{parsed.query}" if parsed.query else ""
        file_name = _slugify(
            f"{self._fetch_counter:02d}_{parsed.netloc}_{path_part}{query_part}"
        )
        html_path = self._html_dir / f"{file_name}.html"
        html_path.write_text(page_content or "", encoding="utf-8")
        return html_path

    def _latest_html_file_for_url(self, url: str) -> str | None:
        for fetch in reversed(self.summary["page_fetches"]):
            if fetch["url"] == url and fetch["html_file"]:
                return fetch["html_file"]
        return None
