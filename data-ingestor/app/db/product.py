import logging
import os
import uuid
from typing import Any, List, Optional
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

from app.models import Product

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

DEFAULT_CATEGORY_NAME = "Uncategorized"


class ProductManager:
    """PostgreSQL manager for the backend app-facing product warehouse tables."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    def _connect(self):
        if psycopg2 is None:
            raise RuntimeError(
                "psycopg2-binary is required for product PostgreSQL writes. "
                "Install data-ingestor requirements."
            )
        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is required for product PostgreSQL writes."
            )

        parsed = urlparse(self.database_url)
        if parsed.scheme and parsed.hostname:
            query = parse_qs(parsed.query)
            return psycopg2.connect(
                dbname=parsed.path.lstrip("/"),
                user=unquote(parsed.username or ""),
                password=unquote(parsed.password or ""),
                host=parsed.hostname,
                port=parsed.port or 5432,
                sslmode=query.get("sslmode", ["require"])[0],
            )

        return psycopg2.connect(self.database_url)

    @staticmethod
    def _product_payload(product: Product | dict[str, Any]) -> dict[str, Any]:
        if isinstance(product, Product):
            data = product.model_dump(mode="json")
        else:
            data = dict(product)

        category_name = str(data.get("category") or "").strip() or DEFAULT_CATEGORY_NAME
        return {
            "title": data["title"],
            "price": float(data["price"]),
            "url": str(data["url"]),
            "image_url": str(data["image_url"]),
            "category": category_name,
        }

    def _get_or_create_category(self, cursor, category_name: Optional[str]) -> str:
        name = str(category_name or "").strip() or DEFAULT_CATEGORY_NAME
        cursor.execute(
            """
            INSERT INTO api_category (id, name)
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            (str(uuid.uuid4()), name),
        )
        return str(cursor.fetchone()["id"])

    def upsert_product(self, product: Product | dict[str, Any]) -> dict[str, Any]:
        """Insert or update a real app product using URL as the idempotency key."""
        payload = self._product_payload(product)
        try:
            with self._connect() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s)::bigint)", (payload["url"],))
                    category_id = self._get_or_create_category(cursor, payload["category"])
                    cursor.execute(
                        """
                        SELECT id
                        FROM api_product
                        WHERE url = %s
                        ORDER BY id::text
                        LIMIT 1
                        FOR UPDATE
                        """,
                        (payload["url"],),
                    )
                    existing_product = cursor.fetchone()

                    if existing_product:
                        cursor.execute(
                            """
                            UPDATE api_product
                            SET
                                title = %s,
                                price = %s,
                                image_url = %s,
                                category_id = %s
                            WHERE id = %s
                            RETURNING id, title, price, url, image_url, category_id
                            """,
                            (
                                payload["title"],
                                payload["price"],
                                payload["image_url"],
                                category_id,
                                existing_product["id"],
                            ),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO api_product (
                                id,
                                title,
                                price,
                                url,
                                image_url,
                                category_id
                            )
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id, title, price, url, image_url, category_id
                            """,
                            (
                                str(uuid.uuid4()),
                                payload["title"],
                                payload["price"],
                                payload["url"],
                                payload["image_url"],
                                category_id,
                            ),
                        )

                    result = dict(cursor.fetchone())
                    logging.info("[UPSERT] Product stored for URL: %s", payload["url"])
                    return result
        except Exception as e:
            logging.error("[UPSERT] Failed to store Product %s: %s", payload.get("url"), e)
            raise

    def create_product(self, product: Product | dict[str, Any]) -> dict[str, Any]:
        """Compatibility wrapper: product writes are upserts into api_product."""
        return self.upsert_product(product)

    def get_product(self, product_id: Optional[str] = None, url: Optional[str] = None) -> Optional[dict]:
        """Fetch a real app product by UUID or URL."""
        if not product_id and not url:
            raise ValueError("product_id or url is required")

        where_clause = "p.url = %s" if url else "p.id::text = %s"
        value = url or product_id

        try:
            with self._connect() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        f"""
                        SELECT
                            p.id,
                            p.title,
                            p.price,
                            p.url,
                            p.image_url,
                            p.category_id,
                            c.name AS category
                        FROM api_product p
                        JOIN api_category c ON c.id = p.category_id
                        WHERE {where_clause}
                        ORDER BY p.id::text
                        LIMIT 1
                        """,
                        (value,),
                    )
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logging.error("[READ] Failed to fetch Product %s: %s", value, e)
            raise

    def get_all_products(self) -> List[dict]:
        """Fetch all real app products."""
        try:
            with self._connect() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT
                            p.id,
                            p.title,
                            p.price,
                            p.url,
                            p.image_url,
                            p.category_id,
                            c.name AS category
                        FROM api_product p
                        JOIN api_category c ON c.id = p.category_id
                        ORDER BY p.title
                        """
                    )
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error("[READ] Failed to fetch Products: %s", e)
            raise

    def update_product(self, product_id: str, changes: dict) -> None:
        """Update supported api_product fields by UUID."""
        allowed_fields = ("title", "price", "url", "image_url")
        assignments = []
        values = []

        for field in allowed_fields:
            if field in changes:
                assignments.append(f"{field} = %s")
                values.append(changes[field])

        try:
            with self._connect() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    category_name = changes.get("category") or changes.get("category_name")
                    if category_name is not None:
                        category_id = self._get_or_create_category(cursor, category_name)
                        assignments.append("category_id = %s")
                        values.append(category_id)

                    if not assignments:
                        logging.info("[UPDATE] No supported Product changes for %s", product_id)
                        return

                    values.append(product_id)
                    query = f"UPDATE api_product SET {', '.join(assignments)} WHERE id::text = %s"
                    cursor.execute(query, values)
                    logging.info("[UPDATE] Product updated: %s", product_id)
        except Exception as e:
            logging.error("[UPDATE] Failed to update Product %s: %s", product_id, e)
            raise

    def delete_product(self, product_id: str) -> None:
        """Delete a real app product by UUID."""
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM api_product WHERE id::text = %s", (product_id,))
                    logging.info("[DELETE] Product deleted: %s", product_id)
        except Exception as e:
            logging.error("[DELETE] Failed to delete Product %s: %s", product_id, e)
            raise

    def mark_product_processed(self, product_id: str) -> None:
        """No-op: api_product does not persist processed state."""
        logging.info("[UPDATE] Ignoring processed state for Product: %s", product_id)

    def get_unprocessed_products(self) -> List[dict]:
        """No-op: api_product does not persist processed state."""
        return []

    def get_products_count(self) -> int:
        """Return the total number of real app products."""
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM api_product")
                    return int(cursor.fetchone()[0])
        except Exception as e:
            logging.error("[COUNT] Failed to count Products: %s", e)
            raise
