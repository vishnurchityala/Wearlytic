import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import AnyHttpUrl
from api.models import Job, JobResult

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
JOBS_COLLECTION_NAME = "scraping_agent_jobs"
JOB_RESULTS_COLLECTION_NAME = "scraping_agent_job_results"

class JobResultsManager:
    """Manager for CRUD operations on scraping job results."""

    def __init__(self):
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        self.collection = db[JOB_RESULTS_COLLECTION_NAME]

    def create_result(self, result: JobResult):
        try:
            result_dict = result.model_dump(mode="json")
            result_dict["_id"] = result_dict["job_id"]
            logging.info(f"Creating Job Result for Job ID: {result.job_id}")
            self.collection.insert_one(result_dict)
        except Exception as e:
            logging.error(f"Failed to create Job Result for Job ID {result.job_id}: {e}")
            raise

    def update_result(self, job_id: str, updates: dict):
        try:
            logging.info(f"Updating Job Result for Job ID: {job_id}")
            return self.collection.update_one({"job_id": job_id}, {"$set": updates})
        except Exception as e:
            logging.error(f"Failed to update Job Result {job_id}: {e}")
            raise

    def get_result(self, job_id: str):
        try:
            logging.info(f"Fetching Job Result for Job ID: {job_id}")
            return self.collection.find_one({"job_id": job_id})
        except Exception as e:
            logging.error(f"Failed to fetch Job Result {job_id}: {e}")
            raise

    def delete_result(self, job_id: str):
        try:
            logging.info(f"Deleting Job Result for Job ID: {job_id}")
            return self.collection.delete_one({"job_id": job_id})
        except Exception as e:
            logging.error(f"Failed to delete Job Result {job_id}: {e}")
            raise
