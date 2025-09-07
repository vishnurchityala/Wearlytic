import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from api.models import Status

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
STATUS_COLLECTION_NAME = os.getenv("STATUS_COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

class StatusManager:
    """CRUD manager for Data Ingestor Status"""

    def __init__(self):
        self.collection = db[STATUS_COLLECTION_NAME]

    def create_status(self, status: Status) -> None:
        try:
            logging.info(f"[CREATE] Inserting Status: {status.id}")
            self.collection.insert_one(status.model_dump(mode="json"))
            logging.info(f"[CREATE] Successfully inserted Status: {status.id}")
        except Exception as e:
            logging.error(f"[CREATE] Failed to insert Status {getattr(status, 'id', '')}: {e}")
            raise

    def update_status(self, status_id: str, changes: dict) -> None:
        try:
            logging.info(f"[UPDATE] Updating Status with ID: {status_id}")
            result = self.collection.update_one({"id": status_id}, {"$set": changes})
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Successfully updated Status: {status_id}")
            else:
                logging.warning(f"[UPDATE] Status not found for update: {status_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to update Status {status_id}: {e}")
            raise

    def get_all_status(self) -> list:
        try:
            logging.info("[READ] Fetching all Status records")
            results = list(self.collection.find())
            logging.info(f"[READ] Total Status records fetched: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch all Status records: {e}")
            raise

    def get_status(self, status_id: str) -> dict | None:
        try:
            logging.info(f"[READ] Fetching Status with ID: {status_id}")
            result = self.collection.find_one({"id": status_id})
            if result:
                logging.info(f"[READ] Status fetched successfully: {status_id}")
            else:
                logging.warning(f"[READ] Status not found: {status_id}")
            return result
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Status {status_id}: {e}")
            raise

    def delete_status(self, status_id: str) -> None:
        try:
            logging.info(f"[DELETE] Deleting Status with ID: {status_id}")
            result = self.collection.delete_one({"id": status_id})
            if result.deleted_count == 1:
                logging.info(f"[DELETE] Successfully deleted Status: {status_id}")
            else:
                logging.warning(f"[DELETE] Status not found for deletion: {status_id}")
        except Exception as e:
            logging.error(f"[DELETE] Failed to delete Status {status_id}: {e}")
            raise

    def get_status_by_status(self, status: str) -> list:
        try:
            logging.info(f"[READ] Fetching Status records with status: {status}")
            results = list(self.collection.find({"status": status}))
            logging.info(f"[READ] Total Status records fetched for status='{status}': {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Status records for status '{status}': {e}")
            raise

    def get_status_by_ingestion_type(self, ingestion_type: str) -> list:
        try:
            logging.info(f"[READ] Fetching Status records with ingestion_type: {ingestion_type}")
            results = list(self.collection.find({"ingestion_type": ingestion_type}))
            logging.info(f"[READ] Total Status records fetched for ingestion_type='{ingestion_type}': {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Status records for ingestion_type '{ingestion_type}': {e}")
            raise
        
    def get_status_status_by_id(self, status_id: str) -> str | None:
        try:
            logging.info(f"[READ] Fetching status value for Status ID: {status_id}")
            document = self.collection.find_one({"id": status_id}, {"status": 1})
            if document and "status" in document:
                logging.info(f"[READ] Found status for Status ID '{status_id}': {document['status']}")
                return document["status"]
            else:
                logging.warning(f"[READ] Status record not found or has no 'status' field for ID: {status_id}")
                return None
        except Exception as e:
            logging.error(f"[READ] Failed to fetch status value for Status ID '{status_id}': {e}")
            raise

