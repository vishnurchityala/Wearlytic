from pydantic import BaseModel, Field, StrictBool
from typing import List
from datetime import datetime
from .listing import Listing

class Source(BaseModel):
    """
    Model class representing a Source with the following attributes:

    - id (str): Unique identifier for the source.  
        Example: "src_001"
    - listings (List[Listing]): List of listing objects associated with the source.  
        Example: [Listing(id="lst_101", source_id="src_001", last_listed=None)]
    - active (bool): Whether the source is active in the system (default: True).  
        Example: True
    - name (str): Human-readable source name for administrators.  
        Example: "Amazon"
    - created_at (datetime): Datetime when the source was created.  
        Example: 2025-06-01 15:20:50.410901+00:00
    - base_url (str): Base URL of the source's main website.  
        Example: "https://www.amazon.in"
    """

    id: str = Field(..., description="Unique identifier for the source.")
    listings: List[Listing] = Field(..., description="List of listing objects associated with the source.")
    active: StrictBool = Field(default=True, description="Whether the source is active in the system (default: True).")
    name: str = Field(..., description="Human-readable source name for administrators.")
    created_at: datetime = Field(..., description="Datetime when the source was created.")
    base_url: str = Field(..., description="Base URL of the source's main website.")
