import os
from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "chatbot_db")

class MongoDBClient:
    """MongoDB client for interacting with the database."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB_NAME]
    
    def get_collections(self) -> List[str]:
        """Get list of collections in the database."""
        return self.db.list_collection_names()
    
    def query_collection(self, collection_name: str, query: Dict[str, Any] = None, 
                         limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Query a collection with optional filtering.
        
        Args:
            collection_name: Name of the collection to query
            query: MongoDB query filter (default: empty query that matches all documents)
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            
        Returns:
            List of documents matching the query
        """
        if query is None:
            query = {}
            
        collection = self.db[collection_name]
        cursor = collection.find(query).limit(limit).skip(skip)
        
        # Convert MongoDB documents to Python dictionaries
        # and remove the MongoDB _id field which is not JSON serializable
        results = []
        for doc in cursor:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            results.append(doc)
            
        return results
    
    def get_document_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by its ID."""
        from bson.objectid import ObjectId
        
        collection = self.db[collection_name]
        try:
            doc = collection.find_one({"_id": ObjectId(document_id)})
            if doc and '_id' in doc:
                doc['_id'] = str(doc['_id'])
            return doc
        except Exception:
            return None
    
    def search_text(self, collection_name: str, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a text search across a collection.
        Note: This requires a text index on the collection.
        """
        collection = self.db[collection_name]
        cursor = collection.find({"$text": {"$search": text}}, 
                                {"score": {"$meta": "textScore"}}).sort(
                                [("score", {"$meta": "textScore"})]).limit(limit)
        
        results = []
        for doc in cursor:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            results.append(doc)
            
        return results
    
    def close(self):
        """Close the MongoDB connection."""
        self.client.close()

# Singleton instance
mongodb_client = MongoDBClient()

def get_mongodb_client() -> MongoDBClient:
    """Get the MongoDB client instance."""
    return mongodb_client 