import os
from urllib.parse import urlparse

import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from app.models import Batch

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")

_client = None
_db = None
_client_pid = None

_TLS_MODE_ENV = "MONGO_TLS_MODE"
_TLS_CA_FILE_ENV = "MONGO_TLS_CA_FILE"


def _is_local_mongo_uri(uri: str | None) -> bool:
    if not uri:
        return False
    try:
        parsed = urlparse(uri)
        hostname = parsed.hostname
    except Exception:
        hostname = None
    if hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return True
    return "localhost" in uri or "127.0.0.1" in uri or "0.0.0.0" in uri


def _mongo_client_kwargs() -> dict:
    tls_mode = (os.getenv(_TLS_MODE_ENV, "auto") or "auto").lower()
    if tls_mode not in {"auto", "true", "false"}:
        tls_mode = "auto"

    use_tls = tls_mode == "true" or (tls_mode == "auto" and not _is_local_mongo_uri(MONGO_URI))
    kwargs = {"serverSelectionTimeoutMS": 5000, "connect": False}

    if use_tls:
        ca_file = os.getenv(_TLS_CA_FILE_ENV) or certifi.where()
        kwargs.update({"tls": True, "tlsCAFile": ca_file})

    return kwargs

def get_client() -> MongoClient:
    global _client
    global _client_pid
    current_pid = os.getpid()
    if _client is None or _client_pid != current_pid:
        if _client is not None:
            _client.close()
        _client = MongoClient(MONGO_URI, **_mongo_client_kwargs())
        _client_pid = current_pid
    return _client

def get_db():
    global _db
    if _db is None:
        _db = get_client()[DB_NAME]
    return _db
