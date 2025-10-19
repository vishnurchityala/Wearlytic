from typing import Optional, Dict, Tuple
from threading import Lock
from scraperkit.base import BaseScraper


class LocalDLLNode:
    def __init__(self, global_node: 'GlobalDLLNode', scraper: BaseScraper, source_website: str):
        """
        Node for doubly linked list of scrapers belonging to a specific source website.
        """
        self.scraper: BaseScraper = scraper
        self.global_node: 'GlobalDLLNode' = global_node
        self.source_website: str = source_website
        self.prev: Optional['LocalDLLNode'] = None
        self.next: Optional['LocalDLLNode'] = None


class GlobalDLLNode:
    def __init__(self, local_node: LocalDLLNode, scraper: BaseScraper, source_website: str):
        """
        Node for global doubly linked list managing all cached scrapers across all sources.
        """
        self.scraper: BaseScraper = scraper
        self.local_node: LocalDLLNode = local_node
        self.source_website: str = source_website
        self.prev: Optional['GlobalDLLNode'] = None
        self.next: Optional['GlobalDLLNode'] = None


class ScraperLRUCache:
    def __init__(self, max_size: int = 17):
        """
        LRU cache managing scraper instances using a global DLL (for LRU tracking)
        and a per-source local DLL (to group scrapers by source website).
        """
        self.global_head: Optional[GlobalDLLNode] = None
        self.global_tail: Optional[GlobalDLLNode] = None
        self.source_dll_map: Dict[str, Tuple[Optional[LocalDLLNode], Optional[LocalDLLNode]]] = {}
        self.max_size = max_size
        self.global_count = 0
        self._lock = Lock()

    def get(self, source_website: str) -> Optional[BaseScraper]:
        """
        Retrieve and remove the most recently added scraper for a given source website.
        This removal ensures the scraper is not simultaneously reused elsewhere.

        Returns:
            Optional[BaseScraper]: The retrieved scraper if available, otherwise None.
        """
        with self._lock:
            local_pair = self.source_dll_map.get(source_website)
            if not local_pair:
                return None

            local_head, local_tail = local_pair
            if not local_tail:
                return None

            local_node = local_tail
            global_node = local_node.global_node
            scraper = global_node.scraper  # Save scraper to return later

            # === Remove from global DLL ===
            if global_node.prev:
                global_node.prev.next = global_node.next
            else:
                self.global_head = global_node.next

            if global_node.next:
                global_node.next.prev = global_node.prev
            else:
                self.global_tail = global_node.prev

            global_node.prev = global_node.next = None

            # === Remove from local DLL ===
            if local_node.prev:
                local_node.prev.next = local_node.next
            else:
                local_head = local_node.next

            if local_node.next:
                local_node.next.prev = local_node.prev
            else:
                local_tail = local_node.prev

            local_node.prev = local_node.next = None

            # Update or delete local DLL entry
            if not local_head and not local_tail:
                del self.source_dll_map[source_website]
            else:
                self.source_dll_map[source_website] = (local_head, local_tail)

            self.global_count -= 1

            # Delete the nodes to free memory
            del global_node
            del local_node

            return scraper

    def insert(self, source_website: str, scraper_object: BaseScraper) -> None:
        """
        Insert a new scraper object into the cache. If cache size exceeds max_size,
        the oldest scraper is evicted from both global and local DLLs.

        Args:
            source_website (str): The source website key to associate this scraper with.
            scraper_object (BaseScraper): The scraper instance to cache.
        """
        with self._lock:
            local_node = LocalDLLNode(global_node=None, scraper=scraper_object, source_website=source_website)
            global_node = GlobalDLLNode(local_node=local_node, scraper=scraper_object, source_website=source_website)
            local_node.global_node = global_node

            # === Add to global DLL tail (newest) ===
            global_node.prev = self.global_tail
            global_node.next = None
            if self.global_tail:
                self.global_tail.next = global_node
            self.global_tail = global_node
            if not self.global_head:
                self.global_head = global_node

            # === Add to local DLL tail (newest) ===
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

            # === Evict if over capacity ===
            if self.global_count > self.max_size:
                self._evict_oldest()

    def _evict_oldest(self) -> None:
        """
        Remove the oldest scraper (global_head) from both the global and local DLLs.
        Called when cache size exceeds max_size.
        """
        oldest_global = self.global_head
        if not oldest_global:
            return

        source_website = oldest_global.source_website

        # === Remove from global DLL ===
        self.global_head = oldest_global.next
        if self.global_head:
            self.global_head.prev = None
        else:
            self.global_tail = None

        self.global_count -= 1

        # === Remove from local DLL ===
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

        local_node.prev = local_node.next = None
        oldest_global.prev = oldest_global.next = None

        # Delete scraper to release resources
        del oldest_global.scraper
        del local_node.scraper

        # Update or remove from source map
        if not local_head and not local_tail:
            del self.source_dll_map[source_website]
        else:
            self.source_dll_map[source_website] = (local_head, local_tail)

        # Delete nodes
        del oldest_global
        del local_node
