from pydantic import BaseModel, AnyHttpUrl, StrictBool, Field
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    """
    Simplified Product model with only critical fields mandatory:
    
    Mandatory:
    - id, title, price, description, url, image_url
    
    Optional:
    - Everything else has defaults or can be None
    """
    # Mandatory fields
    id: str = Field(..., description="Unique identifier for the product.")
    title: str = Field(..., description="Title of the product from the product page.")
    price: float = Field(..., description="Price of the product.")
    description: str = Field(..., description="Description of the product from the product page.")
    url: AnyHttpUrl = Field(..., description="Direct product page URL.")
    image_url: AnyHttpUrl = Field(..., description="URL of the product image.")

    # Optional fields
    category: Optional[str] = Field(default=None, description="Category of the product.")
    gender: Optional[str] = Field(default=None, description="Target gender for the product (e.g., Men, Women, Unisex).")
    colors: Optional[List[str]] = Field(default=None, description="Available color options for the product.")
    sizes: Optional[List[str]] = Field(default=None, description="Available size options for the product.")
    material: Optional[str] = Field(default=None, description="Material composition of the product.")
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="Average customer rating.")
    review_count: Optional[int] = Field(default=None, ge=0, description="Number of customer reviews.")
    processed: StrictBool = Field(default=False, description="Whether the product data has been processed using a LLM.")
    scraped_datetime: Optional[datetime] = Field(default=None, description="Datetime when the product was originally scraped.")
    processed_datetime: Optional[datetime] = Field(default=None, description="Datetime when the product was annotated/processed.")
    page_index: Optional[int] = Field(default=0, description="Position in page where it was scraped.")
    page_content: Optional[str] = Field(default="DEFAULT_PAGE_CONTENT", description="HTML content of the product page.")
