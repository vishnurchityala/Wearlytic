import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from api.models import Listing

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
LISTINGS_COLLECTION_NAME = os.getenv("LISTINGS_COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


class ListingsManager:
    """CRUD manager for Data Ingestor Listing"""
    
    def __init__(self):
        self.collection = db[LISTINGS_COLLECTION_NAME]
    
    def create_listing(self, listing: Listing) -> None:
        try:
            logging.info(f"[CREATE] Inserting Listing: {listing.id}")
            self.collection.insert_one(listing.model_dump(mode="json"))
            logging.info(f"[CREATE] Successfully inserted Listing: {listing.id}")
        except Exception as e:
            logging.error(f"[CREATE] Failed to insert Listing {getattr(listing, 'id', '')}: {e}")
            raise

    def get_listing(self, listing_id: str) -> dict | None:
        try:
            logging.info(f"[READ] Fetching Listing with ID: {listing_id}")
            result = self.collection.find_one({"id": listing_id})
            if result:
                logging.info(f"[READ] Listing fetched successfully: {listing_id}")
            else:
                logging.warning(f"[READ] Listing not found: {listing_id}")
            return result
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Listing {listing_id}: {e}")
            raise

    def get_listings_source(self, source_id: str) -> list:
        try:
            logging.info(f"[READ] Fetching Listings by Source ID: {source_id}")
            results = list(self.collection.find({"source_id": source_id}))
            logging.info(f"[READ] Total Listings fetched for source_id={source_id}: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Listings for Source {source_id}: {e}")
            raise

    def update_listing(self, listing_id: str, changes: dict) -> None:
        try:
            logging.info(f"[UPDATE] Updating Listing with ID: {listing_id}")
            result = self.collection.update_one({"id": listing_id}, {"$set": changes})
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Successfully updated Listing: {listing_id}")
            else:
                logging.warning(f"[UPDATE] Listing not found for update: {listing_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to update Listing {listing_id}: {e}")
            raise

    def delete_listing(self, listing_id: str) -> None:
        try:
            logging.info(f"[DELETE] Deleting Listing with ID: {listing_id}")
            result = self.collection.delete_one({"id": listing_id})
            if result.deleted_count == 1:
                logging.info(f"[DELETE] Successfully deleted Listing: {listing_id}")
            else:
                logging.warning(f"[DELETE] Listing not found for deletion: {listing_id}")
        except Exception as e:
            logging.error(f"[DELETE] Failed to delete Listing {listing_id}: {e}")
            raise
