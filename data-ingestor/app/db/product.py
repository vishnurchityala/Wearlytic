import os
import logging
from typing import List, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from app.models import Product

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")
PRODUCTS_COLLECTION_NAME = os.getenv("PRODUCTS_COLLECTION_NAME", "data_ingestor_products")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


class ProductManager:
    """CRUD manager for Products"""

    def __init__(self):
        self.collection = db[PRODUCTS_COLLECTION_NAME]

    def create_product(self, product: Product) -> None:
        """Insert a new product into the collection"""
        try:
            logging.info(f"[CREATE] Inserting Product: {product.id}")
            product_dict = product.model_dump(mode="json")
            product_dict["_id"] = product_dict["id"]
            self.collection.insert_one(product_dict)
            logging.info(f"[CREATE] Successfully inserted Product: {product.id}")
        except Exception as e:
            logging.error(f"[CREATE] Failed to insert Product {product.id}: {e}")
            raise

    def get_product(self, product_id: str) -> Optional[dict]:
        """Fetch a single product by ID"""
        try:
            logging.info(f"[READ] Fetching Product with ID: {product_id}")
            result = self.collection.find_one({"id": product_id})
            if result:
                logging.info(f"[READ] Product fetched successfully: {product_id}")
            else:
                logging.warning(f"[READ] Product not found: {product_id}")
            return result
        except Exception as e:
            logging.error(f"[READ] Failed to fetch Product {product_id}: {e}")
            raise

    def get_all_products(self) -> List[dict]:
        """Fetch all products"""
        try:
            logging.info("[READ] Fetching all Products")
            results = list(self.collection.find())
            logging.info(f"[READ] Total Products fetched: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch all Products: {e}")
            raise

    def update_product(self, product_id: str, changes: dict) -> None:
        """Update an existing product"""
        try:
            logging.info(f"[UPDATE] Updating Product with ID: {product_id}")
            result = self.collection.update_one({"id": product_id}, {"$set": changes})
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Successfully updated Product: {product_id}")
            else:
                logging.warning(f"[UPDATE] Product not found for update: {product_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to update Product {product_id}: {e}")
            raise

    def delete_product(self, product_id: str) -> None:
        """Delete a product by ID"""
        try:
            logging.info(f"[DELETE] Deleting Product with ID: {product_id}")
            result = self.collection.delete_one({"id": product_id})
            if result.deleted_count == 1:
                logging.info(f"[DELETE] Successfully deleted Product: {product_id}")
            else:
                logging.warning(f"[DELETE] Product not found for deletion: {product_id}")
        except Exception as e:
            logging.error(f"[DELETE] Failed to delete Product {product_id}: {e}")
            raise

    def mark_product_processed(self, product_id: str) -> None:
        """Mark a product as processed and set processed_datetime"""
        from datetime import datetime
        try:
            logging.info(f"[UPDATE] Marking Product as processed: {product_id}")
            result = self.collection.update_one(
                {"id": product_id},
                {"$set": {"processed": True, "processed_datetime": datetime.now()}}
            )
            if result.matched_count == 1:
                logging.info(f"[UPDATE] Product marked as processed: {product_id}")
            else:
                logging.warning(f"[UPDATE] Product not found to mark processed: {product_id}")
        except Exception as e:
            logging.error(f"[UPDATE] Failed to mark Product {product_id} as processed: {e}")
            raise

    def get_unprocessed_products(self) -> List[dict]:
        """Fetch all products that are not yet processed"""
        try:
            logging.info("[READ] Fetching unprocessed Products")
            results = list(self.collection.find({"processed": False}))
            logging.info(f"[READ] Total unprocessed Products fetched: {len(results)}")
            return results
        except Exception as e:
            logging.error(f"[READ] Failed to fetch unprocessed Products: {e}")
            raise
