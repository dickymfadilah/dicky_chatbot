# MongoDB Integration Technical Documentation

This document provides technical details about the MongoDB integration implementation for developers who want to understand, modify, or extend the functionality.

## Architecture Overview

The MongoDB integration consists of several components:

1. **MongoDB Client** (`mongodb_utils.py`): Handles direct interaction with MongoDB
2. **LangChain Tools** (`mongodb_tools.py`): Provides tools for the LangChain agent to interact with MongoDB
3. **API Endpoints** (`main.py`): Exposes MongoDB data through the FastAPI backend
4. **Frontend Integration** (`chatStore.js` and `ChatView.vue`): Provides UI for database interaction

## Component Details

### MongoDB Client (`mongodb_utils.py`)

The `MongoDBClient` class provides a wrapper around PyMongo with methods for common operations:

```python
class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB_NAME]
    
    def get_collections(self) -> List[str]:
        # Returns list of collection names
        
    def query_collection(self, collection_name: str, query: Dict[str, Any] = None, 
                         limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        # Queries a collection with optional filtering
        
    def get_document_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        # Gets a document by its ID
        
    def search_text(self, collection_name: str, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Performs a text search across a collection
```

**Implementation Notes**:
- Uses a singleton pattern to maintain a single database connection
- Handles ObjectId conversion for JSON serialization
- Implements basic error handling for common MongoDB operations

### LangChain Tools (`mongodb_tools.py`)

The MongoDB tools use LangChain's `Tool` class to provide MongoDB operations to the agent:

```python
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
```

**Implementation Notes**:
- Tools are implemented as regular functions rather than classes for better compatibility with LangChain agents
- Each tool function returns JSON strings for consistent handling by the LLM
- The `Tool` class is used to wrap the functions with appropriate names and descriptions
- Error handling is implemented to provide meaningful error messages

### API Integration (`main.py`)

The FastAPI application integrates the MongoDB tools with the LangChain agent:

```python
# Initialize agent with tools
agent = initialize_agent(
    tools=mongodb_tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True
)

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    # Check if the message is asking for database information
    if any(keyword in chat_message.message.lower() for keyword in 
           ["database", "mongodb", "collection", "data", "query", "find", "search"]):
        # Use the agent with tools
        response = agent.run(chat_message.message)
    else:
        # Use the regular conversation chain for non-database queries
        conversation = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=True
        )
        response = conversation.predict(input=chat_message.message)
```

**Implementation Notes**:
- Uses keyword detection to route database queries to the agent
- Provides direct API endpoints for collection listing and querying
- Maintains shared conversation memory between regular chat and database queries

## Agent Workflow

When a user asks a database-related question, the following process occurs:

1. The query is detected as database-related based on keywords
2. The query is passed to the LangChain agent
3. The agent analyzes the query and selects the appropriate tool
4. The tool executes the MongoDB operation
5. Results are returned to the agent, which formulates a natural language response
6. The response is sent back to the user

## Extending the Integration

### Adding New MongoDB Operations

To add a new MongoDB operation:

1. **Add a method to `MongoDBClient`** in `mongodb_utils.py`:

```python
def aggregate_collection(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run an aggregation pipeline on a collection."""
    collection = self.db[collection_name]
    results = list(collection.aggregate(pipeline))
    
    # Process results for JSON serialization
    for doc in results:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
    
    return results
```

2. **Create a new Tool class** in `mongodb_tools.py`:

```python
class AggregationInput(BaseModel):
    """Input for aggregation pipeline."""
    collection_name: str = Field(..., description="Name of the collection")
    pipeline: str = Field(..., description="JSON string of aggregation pipeline")

class AggregationTool(BaseTool):
    """Tool for running aggregation pipelines."""
    name = "run_mongodb_aggregation"
    description = "Runs an aggregation pipeline on a MongoDB collection"
    args_schema: Type[BaseModel] = AggregationInput
    
    def _run(self, collection_name: str, pipeline: str) -> str:
        client = get_mongodb_client()
        
        try:
            pipeline_list = json.loads(pipeline)
            results = client.aggregate_collection(collection_name, pipeline_list)
            return json.dumps(results, default=str)
        except json.JSONDecodeError:
            return "Error: Invalid JSON pipeline"
        except Exception as e:
            return f"Error: {str(e)}"
```

3. **Add the new tool to the tools list** in `mongodb_tools.py`:

```python
def get_mongodb_tools() -> List[BaseTool]:
    """Get all MongoDB tools."""
    return [
        ListCollectionsTool(),
        QueryCollectionTool(),
        GetDocumentTool(),
        SearchTextTool(),
        AggregationTool()  # Add the new tool
    ]
```

### Customizing Query Detection

To modify how database queries are detected:

1. **Update the keyword list** in `main.py`:

```python
database_keywords = [
    "database", "mongodb", "collection", "data", "query", "find", 
    "search", "document", "record", "field", "aggregate", "count",
    "total", "average", "sum", "group", "sort", "filter"
]

if any(keyword in chat_message.message.lower() for keyword in database_keywords):
    # Use the agent with tools
    response = agent.run(chat_message.message)
```

2. **Implement more sophisticated detection** using NLP techniques:

```python
def is_database_query(message: str) -> bool:
    """Determine if a message is a database query using more sophisticated methods."""
    # Simple keyword matching
    if any(keyword in message.lower() for keyword in database_keywords):
        return True
        
    # Check for database operation patterns
    db_patterns = [
        r"show me .+ from .+",
        r"find .+ in .+",
        r"search for .+ in .+",
        r"how many .+ in .+",
        r"list all .+ in .+"
    ]
    
    for pattern in db_patterns:
        if re.search(pattern, message.lower()):
            return True
            
    return False

# In the chat endpoint
if is_database_query(chat_message.message):
    # Use the agent with tools
    response = agent.run(chat_message.message)
```

## Performance Optimization

### Connection Pooling

The MongoDB client uses connection pooling by default. You can configure it by modifying the connection parameters:

```python
self.client = MongoClient(
    MONGODB_URI,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000
)
```

### Query Optimization

For large collections, consider adding projection to return only necessary fields:

```python
def query_collection(self, collection_name: str, query: Dict[str, Any] = None, 
                     projection: Dict[str, Any] = None, limit: int = 10, 
                     skip: int = 0) -> List[Dict[str, Any]]:
    """Query a collection with optional filtering and projection."""
    if query is None:
        query = {}
    if projection is None:
        projection = {}
        
    collection = self.db[collection_name]
    cursor = collection.find(query, projection).limit(limit).skip(skip)
    # Process results...
```

### Caching

Consider implementing caching for frequently accessed data:

```python
from functools import lru_cache

class MongoDBClient:
    # ...
    
    @lru_cache(maxsize=100)
    def get_document_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by its ID with caching."""
        # Implementation...
```

## Security Considerations

### Input Validation

All user inputs should be validated before being used in MongoDB queries:

```python
def validate_collection_name(name: str) -> bool:
    """Validate that a collection name is safe to use."""
    # Check for invalid characters, injection attempts, etc.
    return re.match(r'^[a-zA-Z0-9_]+$', name) is not None

def sanitize_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize a query to prevent injection attacks."""
    # Implement sanitization logic
    return query
```

### Access Control

Implement role-based access control for MongoDB operations:

```python
def check_collection_access(user_id: str, collection_name: str, operation: str) -> bool:
    """Check if a user has access to perform an operation on a collection."""
    # Implement access control logic
    return True  # Replace with actual check
```

## Testing

### Unit Tests

Example unit tests for the MongoDB client:

```python
def test_get_collections():
    """Test that get_collections returns the correct list of collections."""
    client = get_mongodb_client()
    collections = client.get_collections()
    assert isinstance(collections, list)
    # Add more assertions...

def test_query_collection():
    """Test that query_collection returns the correct documents."""
    client = get_mongodb_client()
    results = client.query_collection("test_collection")
    assert isinstance(results, list)
    # Add more assertions...
```

### Integration Tests

Example integration tests for the API endpoints:

```python
async def test_collections_endpoint():
    """Test the /collections endpoint."""
    response = await client.get("/collections")
    assert response.status_code == 200
    data = response.json()
    assert "collections" in data
    # Add more assertions...

async def test_chat_with_db_query():
    """Test a chat message that triggers a database query."""
    response = await client.post("/chat", json={"message": "Show me collections in the database"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    # Add more assertions...
```

## Troubleshooting

### Common Issues and Solutions

1. **Connection Errors**:
   - Check MongoDB service status
   - Verify network connectivity
   - Check firewall settings

2. **Authentication Errors**:
   - Verify credentials in .env file
   - Check user permissions in MongoDB

3. **Query Errors**:
   - Check collection names
   - Verify query syntax
   - Check for invalid field references

### Debugging

Enable verbose logging for troubleshooting:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add logging to MongoDB client
class MongoDBClient:
    def __init__(self):
        self.logger = logging.getLogger("mongodb_client")
        self.logger.info("Initializing MongoDB client")
        # Implementation...
    
    def query_collection(self, collection_name: str, query: Dict[str, Any] = None, 
                         limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        self.logger.debug(f"Querying collection {collection_name} with query {query}")
        # Implementation...
```

## References

- [MongoDB Python Driver Documentation](https://pymongo.readthedocs.io/)
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/agents/tools/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/) 