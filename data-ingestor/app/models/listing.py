from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Listing(BaseModel):
    """
    Model class representing a Listing with the following attributes:

    - id (str): Unique identifier for the listing.  
        Example: "lst_001"
    - source_id (str): Identifier of the parent source associated with the listing.  
        Example: "src_123"
    - last_listed (Optional[datetime]): Datetime when data was last ingested from the listing, or None if not yet ingested.  
        Example: 2025-06-01 15:20:50.410901+00:00
    """

    id: str = Field(..., description="Unique identifier for the listing.")
    source_id: str = Field(..., description="Identifier of the parent source associated with the listing.")
    last_listed: Optional[datetime] = Field(
        default=None,
        description="Datetime when data was last ingested from the listing, or None if not yet ingested."
    )