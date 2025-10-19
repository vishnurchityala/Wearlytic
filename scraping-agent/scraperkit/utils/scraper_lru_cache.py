from typing import Optional, Dict, Tuple
from scraperkit.base import BaseScraper


class LocalDLLNode:
    def __init__(self, global_node: 'GlobalDLLNode', scraper: BaseScraper, source_website: str):
        """
        Node for doubly linked list of scrapers belonging to a specific source website.

        Args:
            global_node (GlobalDLLNode): Corresponding node in the global DLL.
            scraper (BaseScraper): The scraper object stored in this node.
            source_website (str): The source website key this scraper belongs to.
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

        Args:
            local_node (LocalDLLNode): Corresponding node in the local DLL for the scraper.
            scraper (BaseScraper): The scraper object stored in this node.
            source_website (str): The source website key this scraper belongs to.
        """
        self.scraper: BaseScraper = scraper
        self.local_node: LocalDLLNode = local_node
        self.source_website: str = source_website
        self.prev: Optional['GlobalDLLNode'] = None
        self.next: Optional['GlobalDLLNode'] = None


class ScraperLRUCache:
    def __init__(self, max_size: int):
        """
        LRU cache managing scraper instances for multiple source websites using
        two linked lists: a global list tracking overall recency, and local lists
        per source to track scrapers specific to that source.

        Args:
            max_size (int): Maximum number of scraper objects to hold in the cache.
        """
        self.global_head: Optional[GlobalDLLNode] = None  # Oldest scraper in global DLL
        self.global_tail: Optional[GlobalDLLNode] = None  # Newest scraper in global DLL
        self.source_dll_map: Dict[str, Tuple[Optional[LocalDLLNode], Optional[LocalDLLNode]]] = {}
        self.max_size = max_size
        self.global_count = 0  # Current count of scrapers in cache

    def get(self, source_website: str) -> Optional[BaseScraper]:
        """
        Retrieve and remove the most recently added scraper for a given source website.
        This removal ensures the scraper is not simultaneously reused elsewhere.

        Args:
            source_website (str): The source website key to retrieve a scraper for.

        Returns:
            Optional[BaseScraper]: The retrieved scraper if available, otherwise None.
        """
        local_pair = self.source_dll_map.get(source_website)
        if not local_pair:
            return None

        local_head, local_tail = local_pair
        if not local_tail:
            return None

        local_node = local_tail  # Most recently added scraper for this source
        global_node = local_node.global_node

        # Remove from global doubly linked list
        if global_node.prev:
            global_node.prev.next = global_node.next
        else:
            self.global_head = global_node.next

        if global_node.next:
            global_node.next.prev = global_node.prev
        else:
            self.global_tail = global_node.prev

        global_node.prev = global_node.next = None

        # Remove from local doubly linked list
        if local_node.prev:
            local_node.prev.next = local_node.next
        else:
            local_head = local_node.next

        if local_node.next:
            local_node.next.prev = local_node.prev
        else:
            local_tail = local_node.prev

        local_node.prev = local_node.next = None

        # Update or delete the entry in source_dll_map if list is empty
        if not local_head and not local_tail:
            del self.source_dll_map[source_website]
        else:
            self.source_dll_map[source_website] = (local_head, local_tail)

        self.global_count -= 1
        return global_node.scraper

    def insert(self, source_website: str, scraper_object: BaseScraper) -> None:
        """
        Insert a new scraper object into the cache associated with the specified source website.
        The scraper is appended at the tail (newest) of both the global and local doubly linked lists.

        If the cache size exceeds max_size, the oldest scraper is evicted.

        Args:
            source_website (str): The source website key to associate this scraper with.
            scraper_object (BaseScraper): The scraper object to cache.
        """
        local_node = LocalDLLNode(global_node=None, scraper=scraper_object, source_website=source_website)
        global_node = GlobalDLLNode(local_node=local_node, scraper=scraper_object, source_website=source_website)
        local_node.global_node = global_node

        # Add to global DLL tail (newest)
        global_node.prev = self.global_tail
        global_node.next = None
        if self.global_tail:
            self.global_tail.next = global_node
        self.global_tail = global_node
        if not self.global_head:
            self.global_head = global_node

        # Add to local DLL tail (newest)
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

        # Evict oldest if cache size exceeded
        if self.global_count > self.max_size:
            self._evict_oldest()

    def _evict_oldest(self) -> None:
        """
        Remove the oldest scraper from the global doubly linked list and the corresponding
        local doubly linked list. This is called automatically when the cache exceeds max_size.

        Also deletes the scraper object to free resources.
        """
        oldest_global = self.global_head
        if not oldest_global:
            return

        source_website = oldest_global.source_website

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

        local_node.prev = local_node.next = None
        oldest_global.prev = oldest_global.next = None

        # Delete the scraper object to free memory/resources
        del oldest_global.scraper
        del local_node.scraper

        # Update or delete local DLL entry
        if not local_head and not local_tail:
            del self.source_dll_map[source_website]
        else:
            self.source_dll_map[source_website] = (local_head, local_tail)
