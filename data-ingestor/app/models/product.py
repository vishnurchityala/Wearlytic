from pydantic import BaseModel, Field, StrictBool
from typing import List, Optional, Literal
from datetime import datetime

class Product(BaseModel):
    """
    Model class representing a Product with the following attributes:

    - id (str): Unique identifier for the product.  
        Example: "prd_001"
    - url_id (str): Unique URL identifier for the product.  
        Example: "url_789"
    - title (str): Title of the product from the product page.  
        Example: "Men's Cotton Round Neck T-Shirt"
    - price (float): Price of the product.  
        Example: 899.0
    - category (str): Category of the product.  
        Example: "T-Shirts"
    - gender (Literal["Men", "Women", "Unisex"]): Target gender for the product.  
        Example: "Men"
    - url (str): Direct product page URL.  
        Example: "https://www.amazon.in/dp/B0D25JKGJP"
    - image_url (str): URL of the product image.  
        Example: "https://m.media-amazon.com/images/I/81ritEDTS0L._SX679_.jpg"
    - colors (List[str]): List of colors available for the product.  
        Example: ["Red", "Blue", "Black"]
    - size (List[str]): List of available sizes for the product.  
        Example: ["S", "M", "L", "XL"]
    - material (str): Material composition of the product.  
        Example: "100% Cotton"
    - description (str): Description of the product from the product page.  
        Example: "Soft cotton fabric with ribbed round neck."
    - rating (Optional[float]): Average customer rating, or None if unavailable.  
        Example: 4.2
    - review_count (int): Number of customer reviews.  
        Example: 10826
    - processed (StrictBool): Indicates whether the product data has been processed by the annotator.  
        Example: False
    - scraped_datetime (datetime): Datetime when the product was scraped.  
        Example: 2025-06-01 15:20:50.410901+00:00
    - processed_datetime (Optional[datetime]): Datetime when the product was processed, or None if not processed.  
        Example: 2025-06-02 10:15:30.123456+00:00
    - page_index (int): Index of the product on the listing page where it was scraped.  
        Example: 40
    - page_content (str): Raw HTML content of the product page for further parsing.  
        Example: "<html>...</html>"
    """

    id: str = Field(..., description="Unique identifier for the product.")
    url_id: str = Field(..., description="Unique URL identifier for the product.")
    title: str = Field(..., description="Title of the product from the product page.")
    price: float = Field(..., description="Price of the product.")
    category: str = Field(..., description="Category of the product.")
    gender: Literal["Men", "Women", "Unisex"] = Field(..., description="Target gender for the product.")
    url: str = Field(..., description="Direct product page URL.")
    image_url: str = Field(..., description="URL of the product image.")
    colors: List[str] = Field(default_factory=list, description="List of colors available for the product.")
    size: List[str] = Field(default_factory=list, description="List of available sizes for the product.")
    material: str = Field(..., description="Material composition of the product.")
    description: str = Field(..., description="Description of the product from the product page.")
    rating: Optional[float] = Field(default=None, description="Average customer rating, or None if unavailable.")
    review_count: int = Field(default=0, description="Number of customer reviews.")
    processed: StrictBool = Field(default=False, description="Indicates whether the product data has been processed by the annotator.")
    scraped_datetime: datetime = Field(..., description="Datetime when the product was scraped.")
    processed_datetime: Optional[datetime] = Field(default=None, description="Datetime when the product was processed, or None if not processed.")
    page_index: int = Field(default=0, description="Index of the product on the listing page where it was scraped.")
    page_content: str = Field(..., description="Raw HTML content of the product page for further parsing.")