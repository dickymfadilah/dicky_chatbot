from langchain.tools import Tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Type
import json

from .mongodb_utils import get_mongodb_client

class ListCollectionsInput(BaseModel):
    """Input for listing MongoDB collections."""
    pass

class QueryCollectionInput(BaseModel):
    """Input for querying a MongoDB collection."""
    collection_name: str = Field(..., description="Name of the collection to query")
    query: Optional[str] = Field(None, description="JSON string of MongoDB query filter")
    limit: int = Field(10, description="Maximum number of documents to return")
    skip: int = Field(0, description="Number of documents to skip")

class GetDocumentInput(BaseModel):
    """Input for getting a document by ID."""
    collection_name: str = Field(..., description="Name of the collection")
    document_id: str = Field(..., description="ID of the document to retrieve")

class SearchTextInput(BaseModel):
    """Input for text search in MongoDB."""
    collection_name: str = Field(..., description="Name of the collection to search")
    text: str = Field(..., description="Text to search for")
    limit: int = Field(10, description="Maximum number of documents to return")

def list_collections() -> str:
    """Lists all collections in the MongoDB database."""
    client = get_mongodb_client()
    collections = client.get_collections()
    return json.dumps(collections)

def query_collection(collection_name: str, query: Optional[str] = None, 
                    limit: int = 10, skip: int = 0) -> str:
    """Queries a MongoDB collection with optional filtering."""
    client = get_mongodb_client()
    
    # Parse query if provided
    query_dict = None
    if query:
        try:
            query_dict = json.loads(query)
        except json.JSONDecodeError:
            return "Error: Invalid JSON query"
    
    results = client.query_collection(collection_name, query_dict, limit, skip)
    return json.dumps(results, default=str)

def get_document_by_id(collection_name: str, document_id: str) -> str:
    """Gets a document from MongoDB by its ID."""
    client = get_mongodb_client()
    document = client.get_document_by_id(collection_name, document_id)
    
    if document:
        return json.dumps(document, default=str)
    return "Document not found"

def search_text(collection_name: str, text: str, limit: int = 10) -> str:
    """Performs a text search across a MongoDB collection."""
    client = get_mongodb_client()
    results = client.search_text(collection_name, text, limit)
    return json.dumps(results, default=str)

def get_mongodb_tools() -> List[Tool]:
    """Get all MongoDB tools."""
    return [
        Tool(
            name="list_mongodb_collections",
            func=list_collections,
            description="Lists all collections in the MongoDB database"
        ),
        Tool(
            name="query_mongodb_collection",
            func=query_collection,
            description="Queries a MongoDB collection with optional filtering. Args: collection_name, query (optional), limit (default: 10), skip (default: 0)"
        ),
        Tool(
            name="get_mongodb_document",
            func=get_document_by_id,
            description="Gets a document from MongoDB by its ID. Args: collection_name, document_id"
        ),
        Tool(
            name="search_mongodb_text",
            func=search_text,
            description="Performs a text search across a MongoDB collection. Args: collection_name, text, limit (default: 10)"
        )
    ] 