import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from app.models import ProductUrl

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
PRODUCT_URLS_COLLECTION_NAME = os.getenv("PRODUCT_URLS_COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

class ProductUrlManager:
    """CRUD manager for Data Ingestor Product URLs"""

    def __init__(self):
        self.collection = db[PRODUCT_URLS_COLLECTION_NAME]

    def create_product_url(self, product_url: ProductUrl) -> None:
        try:
            logging.info(f"[CREATE] Inserting ProductUrl: {product_url.id}")
            self.collection.insert_one(product_url.model_dump(mode="json"))
            logging.info(f"[CREATE] Successfully inserted ProductUrl: {product_url.id}")
        except Exception as e:
            logging.error(f"[CREATE] Failed to insert ProductUrl {getattr(product_url, 'id', '')}: {e}")
            raise

    def get_product_url(self, product_url_id: str) -> dict | None:
        try:
            logging.info(f"[READ] Fetching ProductUrl with ID: {product_url_id}")
            result = self.collection.find_one({"id": product_url_id})
            if result:
                logging.info(f"[READ] ProductUrl fetched successfully: {product_url_id}")
            else:
                logging.warning(f"[READ] ProductUrl not found: {product_url_id}")
            return result
        except Exception as e:
            logging.error(f"[READ] Failed to fetch ProductUrl {product_url_id}: {e}")
            raise

    def get_product_url_by_source(self, source_id: str) -> list:
        try:
            logging.info(f"[READ] Fetching ProductUrls by Source ID: {source_id}")
            results = list(self.collection.find({"source_id": source_id}))
            logging.info(f"[READ] Total ProductUrls fetched for source_id={source_id}: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch ProductUrls for Source {source_id}: {e}")
            raise

    def get_product_url_by_listing(self, listing_id: str) -> list:
        try:
            logging.info(f"[READ] Fetching ProductUrls by Listing ID: {listing_id}")
            results = list(self.collection.find({"listing_id": listing_id}))
            logging.info(f"[READ] Total ProductUrls fetched for listing_id={listing_id}: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch ProductUrls for Listing {listing_id}: {e}")
            raise

    def get_all_product_urls(self) -> list:
        try:
            logging.info("[READ] Fetching all ProductUrls")
            results = list(self.collection.find())
            logging.info(f"[READ] Total ProductUrls fetched: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch all ProductUrls: {e}")
            raise

    def update_product_url(self, product_url_id: str, changes: dict) -> None:
        try:
            logging.info(f"[UPDATE] Updating ProductUrl with ID: {product_url_id}")
            result = self.collection.update_one({"id": product_url_id}, {"$set": changes})
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Successfully updated ProductUrl: {product_url_id}")
            else:
                logging.warning(f"[UPDATE] ProductUrl not found for update: {product_url_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to update ProductUrl {product_url_id}: {e}")
            raise

    def delete_product_url(self, product_url_id: str) -> None:
        try:
            logging.info(f"[DELETE] Deleting ProductUrl with ID: {product_url_id}")
            result = self.collection.delete_one({"id": product_url_id})
            if result.deleted_count == 1:
                logging.info(f"[DELETE] Successfully deleted ProductUrl: {product_url_id}")
            else:
                logging.warning(f"[DELETE] ProductUrl not found for deletion: {product_url_id}")
        except Exception as e:
            logging.error(f"[DELETE] Failed to delete ProductUrl {product_url_id}: {e}")
            raise
