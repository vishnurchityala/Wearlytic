import logging
from typing import Optional, Dict, Tuple
from threading import Lock
from scraperkit.base import BaseScraper

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class LocalDLLNode:
    def __init__(self, global_node: 'GlobalDLLNode', scraper: BaseScraper, source_website: str):
        self.scraper: BaseScraper = scraper
        self.global_node: 'GlobalDLLNode' = global_node
        self.source_website: str = source_website
        self.prev: Optional['LocalDLLNode'] = None
        self.next: Optional['LocalDLLNode'] = None


class GlobalDLLNode:
    def __init__(self, local_node: LocalDLLNode, scraper: BaseScraper, source_website: str):
        self.scraper: BaseScraper = scraper
        self.local_node: LocalDLLNode = local_node
        self.source_website: str = source_website
        self.prev: Optional['GlobalDLLNode'] = None
        self.next: Optional['GlobalDLLNode'] = None


class ScraperLRUCache:
    def __init__(self, max_size: int = 17):
        self.global_head: Optional[GlobalDLLNode] = None
        self.global_tail: Optional[GlobalDLLNode] = None
        self.source_dll_map: Dict[str, Tuple[Optional[LocalDLLNode], Optional[LocalDLLNode]]] = {}
        self.max_size = max_size
        self.global_count = 0
        self._lock = Lock()

        logger.info(f"Initialized ScraperLRUCache with max_size={max_size}")

    def _log_cache_state(self):
        """Helper to log current cache state for debugging."""
        per_source_counts = {k: self._count_local_nodes(k) for k in self.source_dll_map}
        logger.debug(
            f"Cache state: global_count={self.global_count}, "
            f"num_sources={len(self.source_dll_map)}, per_source_counts={per_source_counts}"
        )

    def _count_local_nodes(self, source_website: str) -> int:
        head, tail = self.source_dll_map.get(source_website, (None, None))
        count = 0
        node = head
        while node:
            count += 1
            node = node.next
        return count

    def get(self, source_website: str) -> Optional[BaseScraper]:
        with self._lock:
            logger.debug(f"Attempting to get scraper for source='{source_website}'")
            local_pair = self.source_dll_map.get(source_website)
            if not local_pair:
                logger.debug(f"No scrapers found for source='{source_website}'")
                return None

            local_head, local_tail = local_pair
            if not local_tail:
                logger.warning(f"Local DLL tail missing for source='{source_website}'")
                return None

            local_node = local_tail
            global_node = local_node.global_node
            scraper = global_node.scraper

            # Remove from global DLL
            if global_node.prev:
                global_node.prev.next = global_node.next
            else:
                self.global_head = global_node.next

            if global_node.next:
                global_node.next.prev = global_node.prev
            else:
                self.global_tail = global_node.prev

            # Remove from local DLL
            if local_node.prev:
                local_node.prev.next = local_node.next
            else:
                local_head = local_node.next

            if local_node.next:
                local_node.next.prev = local_node.prev
            else:
                local_tail = local_node.prev

            if not local_head and not local_tail:
                del self.source_dll_map[source_website]
                logger.debug(f"Removed empty local DLL for source='{source_website}'")
            else:
                self.source_dll_map[source_website] = (local_head, local_tail)

            self.global_count -= 1

            logger.info(
                f"Retrieved scraper from source='{source_website}'. "
                f"Global count now {self.global_count}"
            )
            self._log_cache_state()

            return scraper

    def insert(self, source_website: str, scraper_object: BaseScraper) -> None:
        with self._lock:
            logger.debug(f"Inserting scraper for source='{source_website}'")

            local_node = LocalDLLNode(global_node=None, scraper=scraper_object, source_website=source_website)
            global_node = GlobalDLLNode(local_node=local_node, scraper=scraper_object, source_website=source_website)
            local_node.global_node = global_node

            # Add to global DLL
            global_node.prev = self.global_tail
            global_node.next = None
            if self.global_tail:
                self.global_tail.next = global_node
            self.global_tail = global_node
            if not self.global_head:
                self.global_head = global_node

            # Add to local DLL
            local_head, local_tail = self.source_dll_map.get(source_website, (None, None))
            local_node.prev = local_tail
            local_node.next = None
            if local_tail:
                local_tail.next = local_node
            local_tail = local_node
            if not local_head:
                local_head = local_node

            self.source_dll_map[source_website] = (local_head, local_tail)
            self.global_count += 1

            logger.info(
                f"Inserted scraper for source='{source_website}'. "
                f"Global count={self.global_count}"
            )

            if self.global_count > self.max_size:
                logger.warning("Cache size exceeded max_size. Evicting oldest scraper.")
                self._evict_oldest()

            self._log_cache_state()

    def _evict_oldest(self) -> None:
        oldest_global = self.global_head
        if not oldest_global:
            logger.warning("Eviction attempted on empty cache.")
            return

        source_website = oldest_global.source_website
        logger.info(f"Evicting oldest scraper from source='{source_website}'")

        # Remove from global DLL
        self.global_head = oldest_global.next
        if self.global_head:
            self.global_head.prev = None
        else:
            self.global_tail = None

        self.global_count -= 1

        # Remove from local DLL
        local_node = oldest_global.local_node
        local_head, local_tail = self.source_dll_map.get(source_website, (None, None))

        if local_node.prev:
            local_node.prev.next = local_node.next
        else:
            local_head = local_node.next

        if local_node.next:
            local_node.next.prev = local_node.prev
        else:
            local_tail = local_node.prev

        if not local_head and not local_tail:
            del self.source_dll_map[source_website]
            logger.debug(f"Removed empty local DLL for source='{source_website}' after eviction")
        else:
            self.source_dll_map[source_website] = (local_head, local_tail)

        logger.info(f"Eviction complete. Global count={self.global_count}")
        self._log_cache_state()
