from pydantic import BaseModel, Field, StrictBool
from typing import Optional
from datetime import datetime

class Listing(BaseModel):
    """
    Represents a listing entity with its core metadata.

    Attributes:
        id (str): Unique identifier for the listing.
            Example: "lst_001"
        source_id (str): Identifier for the parent source associated with the listing.
            Example: "src_123"
        last_listed (Optional[datetime]): Timestamp of the most recent data ingestion 
            from this listing. If the listing hasn't been ingested yet, this will be None.
            Example: 2025-06-01 15:20:50.410901+00:00
        url (str): URL of the listing.
        active (StrictBool): Whether the listing is currently active. Defaults to False.
    """

    id: str = Field(..., description="Unique identifier for the listing.")
    source_id: str = Field(..., description="Identifier of the parent source associated with the listing.")
    last_listed: Optional[datetime] = Field(
        default=None,
        description="Datetime when data was last ingested from the listing, or None if not yet ingested."
    )
    url: str = Field(..., description="URL of the listing.")
    active: StrictBool = Field(
        default=False,
        description="Indicates whether the listing is currently active."
    )
