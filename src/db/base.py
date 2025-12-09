from __future__ import annotations
from functools import lru_cache
import os
from typing import Optional

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_DB_NAME = "task_manager"
TASKS_COLLECTION_NAME = "tasks"

def _get_mongo_uri() -> str:
    """
    Resolve the MongoDB URI from environment variables, falling back to a
    sensible default for local development.
    """
    return os.getenv("MONGO_URI") or DEFAULT_MONGO_URI


def _get_db_name() -> str:
    """
    Resolve the database name from environment variables, falling back to a
    sensible default.
    """
    return os.getenv("DB_NAME") or DEFAULT_DB_NAME


@lru_cache(maxsize=1)
def get_client(uri: Optional[str] = None) -> MongoClient:
    """
    Return a process-wide MongoClient instance.

    The client is cached so repeated calls reuse the same underlying
    connection pool. An explicit `uri` overrides environment defaults.
    """
    return MongoClient(uri or _get_mongo_uri())


def get_database(name: Optional[str] = None) -> Database:
    """
    Return the primary application database.

    The name can be overridden, but typically you rely on environment
    variables or the default.
    """
    client = get_client()
    return client[name or _get_db_name()]


def get_tasks_collection() -> Collection:
    """
    Convenience accessor for the `tasks` collection used by TaskService.
    """
    db = get_database()
    collection = db[TASKS_COLLECTION_NAME]

    collection.create_index([("status", ASCENDING)])
    collection.create_index([("priority_level", ASCENDING)])
    collection.create_index([("due_date", ASCENDING)])

    return collection


def close_client() -> None:
    """
    Close the cached MongoClient, if it has been created.

    This is primarily useful for long-lived processes or tests that need
    to clean up connections explicitly. For short-lived CLI usage, it is
    usually safe to omit calling this.
    """
    
    cache = get_client.cache_info()
    if cache.hits or cache.misses:
        
        client = get_client()
        client.close()
        get_client.cache_clear()


