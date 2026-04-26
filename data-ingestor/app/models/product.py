from pydantic import BaseModel, Field, StrictBool
from typing import List, Optional, Literal
from datetime import datetime

class Product(BaseModel):
    """
    Simplified Product model:

    Mandatory fields:
    - id, url_id, title, price, url, image_url

    Optional fields:
    - Everything else has defaults or can be None
    """

    # Mandatory fields
    id: str = Field(..., description="Unique identifier for the product.")
    url_id: str = Field(..., description="Unique URL identifier for the product.")
    title: str = Field(..., description="Title of the product from the product page.")
    price: float = Field(..., description="Price of the product.")
    url: str = Field(..., description="Direct product page URL.")
    image_url: str = Field(..., description="URL of the product image.")

    # Optional fields
    category: Optional[str] = Field(default=None, description="Category of the product.")
    gender: Optional[Literal["Men", "Women", "Unisex"]] = Field(default=None, description="Target gender for the product.")
    colors: List[str] = Field(default_factory=list, description="List of colors available for the product.")
    size: List[str] = Field(default_factory=list, description="List of available sizes for the product.")
    material: Optional[str] = Field(default=None, description="Material composition of the product.")
    description: Optional[str] = Field(default=None, description="Description of the product from the product page.")
    rating: Optional[float] = Field(default=None, description="Average customer rating, or None if unavailable.")
    review_count: int = Field(default=0, description="Number of customer reviews.")
    processed: StrictBool = Field(default=False, description="Indicates whether the product data has been processed by the annotator.")
    scraped_datetime: Optional[datetime] = Field(default=None, description="Datetime when the product was scraped.")
    processed_datetime: Optional[datetime] = Field(default=None, description="Datetime when the product was processed, or None if not processed.")
    page_index: int = Field(default=0, description="Index of the product on the listing page where it was scraped.")
    page_content: Optional[str] = Field(default=None, description="Raw HTML content of the product page for further parsing.")
