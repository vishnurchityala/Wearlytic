from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Batch(BaseModel):
    """
    Model class representing a Batch with the following attributes:

    - id (str): Unique identifier for the batch.  
        Example: "batch_001"
    - batch_size (int): Number of product URLs in the batch.  
        Example: 10
    - urls (List[str]): List of product URL IDs associated with the batch.  
        Example: ["url_1", "url_2"]
    - last_processed (Optional[datetime]): Datetime when the batch was last processed, or None if not processed yet.  
        Example: 2025-06-01 15:20:50.410901+00:00
    """
    id: str = Field(..., description="Unique identifier for the batch.")
    batch_size: int = Field(..., description="Number of product URLs in the batch.")
    urls: List[str] = Field(..., description="List of product URL IDs associated with the batch.")
    last_processed: Optional[datetime] = Field(
        default=None,
        description="Datetime when the batch was last processed, or None if not processed yet."
    )
