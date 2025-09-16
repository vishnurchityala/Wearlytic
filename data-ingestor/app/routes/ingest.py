from fastapi import APIRouter, Request, Form, status

router = APIRouter()


"""
Ingest Listing Route:

Request Body = { JobID:  1de6a864-0ec2-40c9-8ce5-f825bfe18126 }

Flow 
--> ScrapingAgent DB Access to get the job status and job type, if failed flag the status as failed in DataIngestor.
--> ScrapingAgent DB Access to get the result body if job success.
--> DatatIngestor DB Access to get the parent listing_id if listing and batch_id if product.
--> DataIngestor DB Access to push the result according result type.

"""

# Ingest Product Route