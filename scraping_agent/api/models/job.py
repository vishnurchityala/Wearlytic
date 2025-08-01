from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Literal, Optional, Union
from datetime import datetime
from .product import Product
from .listing import Listing

class JobRequest(BaseModel):
    """
        Model representing a job request for scraping a webpage.

        - webpage_url (AnyHttpUrl): The URL of the webpage to be scraped.
        - priority (Literal['high', 'medium', 'low']): The priority level of the job request. Defaults to 'low'.
        - type_page (Literal['listing', 'product']): The type of page to be scraped, either a listing page or a product page.
    """
    webpage_url: AnyHttpUrl = Field(...)
    priority: Literal['high', 'medium', 'low'] = Field(default='low')
    type_page: Literal['listing', 'product'] = Field(...)

class Job(BaseModel):
    """
        Model class representing a Job with the following attributes:

        - job_id: Unique identifier for the job.
        - webpage_url: The URL of the webpage to be processed.
        - priority: Priority level of the job. Can be 'high', 'medium', or 'low'. Default is 'low'.
        - type_page: Type of the page to be processed. Can be 'listing' or 'product'.
        - status: Current status of the job. Can be 'queued', 'processing', 'completed', or 'failed'.
        - created_at: Datetime when the job was created.
        - completed_at: Datetime when the job was completed (optional).
        - error_message: Error message if the job failed (optional).
    """
    job_id: str
    webpage_url: AnyHttpUrl = Field(...)
    priority: Literal['high', 'medium', 'low'] = Field(default='low')
    type_page: Literal['listing', 'product'] = Field(...)
    status: Literal['queued', 'processing', 'completed', 'failed'] = Field(...)
    created_at: datetime = Field(...)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class JobResult(BaseModel):
    """
    Model representing the result of a completed job.

    - job_id: Unique identifier for the job.
    - result: The result of the job, which can be either a Product or Listing object.
    - status: Status of the job when the result was produced.
    - completed_at: Datetime when the job was completed.
    - error_message: Error message if the job failed (optional).
    """
    job_id: str = Field(...)
    result: Union[Product, Listing] = Field(...)
    status: Literal['completed', 'failed'] = Field(...)
    completed_at: datetime = Field(...)
    error_message: Optional[str] = None