import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from app.models import Source
from app.models import Listing

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
SOURCES_COLLECTION_NAME = os.getenv("SOURCES_COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


class SourceManager:
    """CRUD manager for Data Ingestor Source"""

    def __init__(self):
        self.collection = db[SOURCES_COLLECTION_NAME]
    
    def create_source(self, source: Source) -> None:
        try:
            logging.info(f"[CREATE] Inserting Source: {source.id}")
            source_dict = source.model_dump(mode="json")
            source_dict["_id"] = source_dict['id']
            self.collection.insert_one(source_dict)
            logging.info(f"[CREATE] Successfully inserted Source: {source.id}")
        except Exception as e:
            logging.error(f"[CREATE] Failed to insert Source {getattr(source, 'id', '')}: {e}")
            raise
    
    def add_listing_to_source(self, source_id: str, listing_id: str) -> None:
        try:
            logging.info(f"[CREATE] Adding Listing with ID: {listing_id} to Source: {source_id}")

            update_result = self.collection.update_one(
                {"id": source_id},
                {
                    "$addToSet": {"listings": listing_id},
                    "$inc": {"listing_count": 1}
                }
            )
            if update_result.matched_count == 0:
                logging.warning(f"[CREATE] No source found with ID: {source_id}")
            else:
                logging.info(f"[CREATE] Successfully added Listing {listing_id} to Source {source_id}")

        except Exception as e:
            logging.error(f"[CREATE] Failed to add Listing {listing_id} to Source {source_id}: {e}")
            raise


    def get_source(self, source_id: str) -> dict | None:
        try:
            logging.info(f"[READ] Fetching Source with ID: {source_id}")
            result = self.collection.find_one({'id': source_id})
            if result:
                logging.info(f"[READ] Source fetched successfully: {source_id}")
            else:
                logging.warning(f"[READ] Source not found: {source_id}")
            return result
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Source {source_id}: {e}")
            raise

    def get_sources(self) -> list:
        try:
            logging.info("[READ] Fetching all Sources")
            results = list(self.collection.find())
            logging.info(f"[READ] Total Sources fetched: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch all Sources: {e}")
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
    
    def get_status_by_status(self, status: str) -> list:
        try:
            logging.info(f"[READ] Fetching Status records with status: {status}")
            results = list(self.collection.find({"status": status}))
            logging.info(f"[READ] Total Status records fetched for status='{status}': {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Status records for status '{status}': {e}")
            raise

    def delete_source(self, source_id: str) -> None:
        try:
            logging.info(f"[DELETE] Deleting Source with ID: {source_id}")
            result = self.collection.delete_one({"id": source_id})
            if result.deleted_count == 1:
                logging.info(f"[DELETE] Successfully deleted Source: {source_id}")
            else:
                logging.warning(f"[DELETE] Source not found for deletion: {source_id}")
        except Exception as e:
            logging.error(f"[DELETE] Failed to delete Source {source_id}: {e}")
            raise

    def update_source(self, source_id: str, changes: dict) -> None:
        try:
            logging.info(f"[UPDATE] Updating Source with ID: {source_id}")
            result = self.collection.update_one({"id": source_id}, {"$set": changes})
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Successfully updated Source: {source_id}")
            else:
                logging.warning(f"[UPDATE] Source not found for update: {source_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to update Source {source_id}: {e}")
            raise
        
    def remove_listing_from_source(self, source_id: str, listing_id: str) -> None:
        try:
            logging.info(f"[DELETE] Removing Listing with ID: {listing_id} from Source: {source_id}")
            
            update_result = self.collection.update_one(
                {"id": source_id},
                {
                    "$pull": {"listings": listing_id},
                    "$inc": {"listing_count": -1}
                }
            )

            if update_result.matched_count == 0:
                logging.warning(f"[DELETE] No source found with ID: {source_id}")
            elif update_result.modified_count == 0:
                logging.warning(f"[DELETE] Listing ID: {listing_id} not found in source {source_id}")
            else:
                logging.info(f"[DELETE] Successfully removed Listing {listing_id} from Source {source_id}")
                
        except Exception as e:
            logging.error(f"[DELETE] Failed to remove Listing {listing_id} from Source {source_id}: {e}")
            raise
