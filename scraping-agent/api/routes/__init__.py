from .scrape import router as ScrapeRouter
from .status import router as StatusRouter
from .base import router as IndexRouter

__all__ = ["ScrapeRouter","StatusRouter","IndexRouter"]