from pydantic import BaseModel, Field, StrictBool
from typing import Optional

class ProductUrl(BaseModel):
    """
    Model class representing a Product URL with the following attributes:

    - id (str): Unique identifier for the product URL.  
        Example: "url_001"
    - url (str): Direct product page URL.  
        Example: "https://www.amazon.in/dp/B0D25JKGJP"
    - source_id (str): Identifier of the source associated with this product URL.  
        Example: "src_123"
    - listing_id (str): Identifier of the listing associated with this product URL.  
        Example: "lst_456"
    - page_index (int): Index of the page from which the product URL was scraped.  
        Example: 2
    - batched (StrictBool): Indicates whether the product URL has been added to a batch (default: False).  
        Example: True
    - batch_id (Optional[str]): Identifier of the batch to which this product URL belongs, if any.  
        Example: "batch_789"
    """

    id: str = Field(..., description="Unique identifier for the product URL.")
    url: str = Field(..., description="Direct product page URL.")
    source_id: str = Field(..., description="Identifier of the source associated with this product URL.")
    listing_id: str = Field(..., description="Identifier of the listing associated with this product URL.")
    page_index: int = Field(..., description="Index of the page from which the product URL was scraped.")
    batched: StrictBool = Field(default=False, description="Indicates whether the product URL has been added to a batch (default: False).")
    batch_id: Optional[str] = Field(default=None, description="Identifier of the batch to which this product URL belongs, if any.")
