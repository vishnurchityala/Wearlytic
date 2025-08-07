from pydantic import BaseModel, AnyHttpUrl, Field
from typing import List

class ListingItem(BaseModel):
    """
    ListingItem model represents a web listing with its URL and associated page rank.

    Attributes:
        url (AnyHttpUrl): The URL of the listing. Must be a valid HTTP/HTTPS URL.
        page_rank (float): Page rank score for the listing. Must be greater than or equal to 0.0.
    """
    url: AnyHttpUrl
    page_rank: float = Field(..., ge=0.0, description="Page rank score (must be >= 0.0)")

class Listing(BaseModel):
    """
    Listing model representing a paginated collection of listing items.

    Attributes:
        items (List[ListingItem]): List of URLs with their corresponding page rank.
        page_index (int): Index of the current page (must be >= 0).
    """
    items: List[ListingItem] = Field(..., description="List of URLs with page rank")
    page_index: int = Field(0, ge=0, description="Index of the page (must be >= 0)")