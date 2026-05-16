from typing import Optional
import os
from urllib.parse import urlparse
import mimetypes


class SupabaseBucketManager:
    """
    Supabase Storage bucket manager.
    - Upload bytes
    - Upload local files
    - Delete by path
    - Delete by URL
    - Get public URL
    """

    def __init__(self, supabase_url: str, supabase_key: str, bucket_name: str):
        from supabase import create_client

        self.supabase_url = supabase_url.rstrip("/")
        self.supabase_key = supabase_key
        self.bucket_name = bucket_name

        self._client = create_client(self.supabase_url, self.supabase_key)

    @classmethod
    def from_env(cls, bucket_name: Optional[str] = None) -> "SupabaseBucketManager":
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not supabase_url or not supabase_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        final_bucket = bucket_name or os.environ.get("SUPABASE_BUCKET", "generated-images")
        return cls(supabase_url=supabase_url, supabase_key=supabase_key, bucket_name=final_bucket)

    def store_bytes(self, object_bytes: bytes, object_path: str, *, upsert: bool = True, content_type: Optional[str] = None) -> str:
        """Upload raw bytes to the bucket. Upserts by default if the object exists."""
        storage = self._client.storage.from_(self.bucket_name)
        # Normalize path to avoid leading slash issues
        normalized_path = object_path.lstrip("/")
        if content_type is None:
            guessed_type, _ = mimetypes.guess_type(object_path)
            content_type = guessed_type
        file_options = {}
        # Some client versions require header values to be strings
        # Convert upsert bool to "true"/"false" strings to be safe
        file_options["upsert"] = "true" if upsert else "false"
        if content_type:
            file_options["contentType"] = content_type
        storage.upload(normalized_path, object_bytes, file_options=file_options)
        return storage.get_public_url(normalized_path)

    def store_file(self, file_path: str, object_path: str) -> str:
        """Upload a local file to the bucket."""
        with open(file_path, "rb") as f:
            data = f.read()
        return self.store_bytes(data, object_path)

    def delete_path(self, object_path: str) -> bool:
        """Delete an object by its bucket-relative path."""
        storage = self._client.storage.from_(self.bucket_name)
        storage.remove([object_path])
        return True

    def delete_by_url(self, file_url: str) -> bool: 
        """Delete an object using its Supabase URL."""
        path = self._extract_object_path_from_url(file_url)
        if not path:
            return False
        return self.delete_path(path)

    def _extract_object_path_from_url(self, file_url: str) -> Optional[str]:
        try:
            parsed = urlparse(file_url)
            path = parsed.path
            marker = "/storage/v1/object/"
            idx = path.find(marker)
            if idx == -1:
                return None
            remainder = path[idx + len(marker):]
            parts = remainder.split("/", 2)
            if len(parts) < 3:
                return None
            _, bucket, object_path = parts
            if bucket != self.bucket_name:
                return None
            return object_path
        except Exception:
            return None
