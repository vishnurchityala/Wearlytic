from pydantic import BaseModel, Field
from typing import Literal

class Status(BaseModel):
    """
    Model class representing the status of an ingestion process with the following attributes:

    - id (str): Unique identifier for the ingestion process.  
        Example: "ing_001"
    - ingestion_type (Literal["listing", "product"]): Type of ingestion, either "listing" or "product".  
        Example: "listing"
    - job_id (str): ScrapingAgent job identifier for the background task.  
        Example: "job_12345"
    - status (Literal["processing", "completed", "failed"]): Current status of the ingestion process.  
        Example: "processing"
    """

    id: str = Field(..., description="Unique identifier for the ingestion process.")
    ingestion_type: Literal["listing", "product"] = Field(..., description="Type of ingestion, either 'listing' or 'product'.")
    job_id: str = Field(..., description="ScrapingAgent job identifier for the background task.")
    status: Literal["processing", "completed", "failed"] = Field(..., description="Current status of the ingestion process.")