from pydantic import BaseModel, AnyHttpUrl, StrictBool, Field
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    """
    Model class representing a Product with the following attributes:

    - Title: Name of the product -- Jockey 2715 Men's Super Combed Cotton Rich Striped Regular Fit Round Neck Half Sleeve T-Shirt
    - ID: Unique identifier for the product -- amzn_BU3872
    - Price: Price of the Product -- 899
    - Category: Category to which the product belongs  -- T-Shirts
    - Gender: Target gender for the product (e.g., Men, Women, Unisex) -- Men
    - URL: Direct link to the product page -- https://www.amazon.in/dp/B0D25JKGJP
    - Image URL: Link to the product image -- https://m.media-amazon.com/images/W/MEDIAX_1215821-T1/images/I/81ritEDTS0L._SX679_.jpg
    - Colors: Available color options for the product -- [ Red, Blue, Black, White, Yellow ]
    - Sizes: Available size options for the product -- [ XS, S, M, L, XL, XXL ]
    - Material: Material composition of the product -- Super Combed Cotton Rich
    - Description: Detailed description of the product  -- Super combed Cotton Rich fabric. Ribbed round neck to prevent sagging.
    - Rating: Average customer rating -- 4.2
    - Review Count: Number of customer reviews -- 10,826
    - Processed: Whether the product data has been processed using a LLM -- False
    - Scraped Datetime: Datetime when the product was originally scraped -- 2025-06-01 15:20:50.410901+00:00
    - Processed Datetime: Datetime when the product was annotated/processed -- 2025-06-01 15:20:50.410901+00:00
    - Page Index -- 40 This indicates the position in page it was scraped.
    """
    id: str = Field(...)
    title: str = Field(...)
    price: float = Field(...)
    category: str = Field(...)
    gender: Optional[str]
    url: AnyHttpUrl = Field(...)
    image_url: AnyHttpUrl = Field(...)
    colors: List[str] = Field(...)
    sizes: List[str] = Field(...)
    material: str = Field(...)
    description: str = Field(...)
    rating: float = Field(default=0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    processed: StrictBool = Field(default=False)
    scraped_datetime: Optional[datetime]
    processed_datetime: Optional[datetime]
    page_index: Optional[int] = 0