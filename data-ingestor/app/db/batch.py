import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from app.models import Batch

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
BATCHES_COLLECTION_NAME = os.getenv("BATCHES_COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

class BatchManager:
    """CRUD manager for Data Ingestor Batch"""

    def __init__(self):
        self.collection = db[BATCHES_COLLECTION_NAME]

    def create_batch(self, batch: Batch) -> None:
        try:
            logging.info(f"[CREATE] Inserting Batch: {batch.id}")
            self.collection.insert_one(batch.model_dump(mode="json"))
            logging.info(f"[CREATE] Successfully inserted Batch: {batch.id}")
        except Exception as e:
            logging.error(f"[CREATE] Failed to insert Batch {getattr(batch, 'id', '')}: {e}")
            raise

    def get_all_batches(self) -> list:
        try:
            logging.info("[READ] Fetching all Batches")
            results = list(self.collection.find())
            logging.info(f"[READ] Total Batches fetched: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch all Batches: {e}")
            raise

    def get_batch_by_id(self, batch_id: str) -> dict | None:
        try:
            logging.info(f"[READ] Fetching Batch with ID: {batch_id}")
            result = self.collection.find_one({"id": batch_id})
            if result:
                logging.info(f"[READ] Batch fetched successfully: {batch_id}")
            else:
                logging.warning(f"[READ] Batch not found: {batch_id}")
            return result
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Batch {batch_id}: {e}")
            raise

    def get_last_processed_batch_id(self) -> str | None:
        try:
            logging.info("[READ] Fetching batch_id of the last processed batch")
            batch = self.collection.find_one(
                {"last_processed": {"$ne": None}},
                sort=[("last_processed", -1)],
                projection={"id": 1}
            )
            if batch and "id" in batch:
                logging.info(f"[READ] Last processed batch_id: {batch['id']}")
                return batch["id"]
            else:
                logging.warning("[READ] No processed batches found")
                return None
        except Exception as e:
            logging.error(f"[READ] Failed to fetch last processed batch_id: {e}")
            raise

    def get_last_processed_batch(self) -> Batch | None:
        try:
            logging.info("[READ] Fetching last processed batch document")
            batch = self.collection.find_one(
                {"last_processed": {"$ne": None}},
                sort=[("last_processed", -1)]
            )
            if batch:
                batch.pop("_id", None)
                logging.info(f"[READ] Last processed batch fetched, batch_id: {batch.get('id', 'Unknown')}")
                return Batch(**batch)
            else:
                logging.warning("[READ] No processed batches found")
                return None
        except Exception as e:
            logging.error(f"[READ] Failed to fetch last processed batch: {e}")
            raise

    def update_batch(self, batch_id: str, changes: dict) -> None:
        try:
            logging.info(f"[UPDATE] Updating Batch with ID: {batch_id}")
            result = self.collection.update_one({"id": batch_id}, {"$set": changes})
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Successfully updated Batch: {batch_id}")
            else:
                logging.warning(f"[UPDATE] Batch not found for update: {batch_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to update Batch {batch_id}: {e}")
            raise

    def add_product_url(self, batch_id: str, product_url_id: str) -> None:
        try:
            logging.info(f"[UPDATE] Adding ProductUrl '{product_url_id}' to Batch: {batch_id}")
            result = self.collection.update_one(
                {"id": batch_id},
                {"$addToSet": {"urls": product_url_id}, "$inc": {"batch_size": 1}}
            )
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Successfully added ProductUrl '{product_url_id}' to Batch: {batch_id}")
            else:
                logging.warning(f"[UPDATE] Batch not found for adding ProductUrl: {batch_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to add ProductUrl '{product_url_id}' to Batch {batch_id}: {e}")
            raise

    def get_batch_size(self, batch_id: str) -> int | None:
        try:
            logging.info(f"[READ] Fetching batch_size for Batch: {batch_id}")
            batch = self.collection.find_one({"id": batch_id}, {"batch_size": 1})
            if batch and "batch_size" in batch:
                logging.info(f"[READ] Batch size for {batch_id}: {batch['batch_size']}")
                return batch["batch_size"]
            else:
                logging.warning(f"[READ] Batch not found or batch_size missing: {batch_id}")
                return None
        except Exception as e:
            logging.error(f"[READ] Failed to fetch batch_size for Batch {batch_id}: {e}")
            raise

    def delete_batch(self, batch_id: str) -> None:
        try:
            logging.info(f"[DELETE] Deleting Batch with ID: {batch_id}")
            result = self.collection.delete_one({"id": batch_id})
            if result.deleted_count == 1:
                logging.info(f"[DELETE] Successfully deleted Batch: {batch_id}")
            else:
                logging.warning(f"[DELETE] Batch not found for deletion: {batch_id}")
        except Exception as e:
            logging.error(f"[DELETE] Failed to delete Batch {batch_id}: {e}")
            raise

    def get_batch_with_space(self, capacity: int = 100) -> dict | None:
        """
        Fetch a batch that has space for more ProductUrls.
        Default maximum capacity is 100.

        Args:
            capacity (int): Maximum allowed batch size (default=100).

        Returns:
            dict | None: Batch document with available space, or None if none found.
        """
        try:
            logging.info(f"[READ] Fetching a batch with space (capacity < {capacity})")
            batch = self.collection.find_one(
                {"batch_size": {"$lt": capacity}},
                sort=[("created_at", 1)]  # Optional: choose oldest batch first
            )
            if batch:
                logging.info(f"[READ] Found batch with available space: {batch.get('id', 'Unknown')}")
                return batch
            else:
                logging.warning("[READ] No batches with available space found")
                return None
        except Exception as e:
            logging.error(f"[READ] Failed to fetch batch with space: {e}")
            raise
