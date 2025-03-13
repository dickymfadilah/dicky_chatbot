# MongoDB Integration for LangChain Ollama Chatbot

This guide explains how to set up, configure, and use the MongoDB integration with your LangChain Ollama Chatbot. This integration allows your chatbot to access and query data from MongoDB collections when asked.

## Prerequisites

- MongoDB server installed and running (version 4.0 or higher recommended)
- MongoDB database created for the chatbot
- Basic knowledge of MongoDB operations and queries
- Python 3.8+ and Node.js 14+ installed

## Installation

1. **Install Backend Dependencies**:

```bash
cd LangchainBackend
pip install -r requirements.txt
```

2. **Install Frontend Dependencies**:

```bash
cd ClientFrontend
npm install
```

## Configuration

### Backend Configuration

1. **Update the .env file in the LangchainBackend directory**:

```
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3
MONGODB_URI=mongodb://username:password@your-mongodb-host:27017
MONGODB_DB_NAME=your_database_name
```

Replace `mongodb://username:password@your-mongodb-host:27017` with your actual MongoDB connection string and `your_database_name` with your database name.

2. **Connection String Formats**:

- **Local MongoDB**: `mongodb://localhost:27017`
- **MongoDB Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/`
- **With Authentication**: `mongodb://username:password@host:port/`
- **With Options**: `mongodb://host:port/?retryWrites=true&w=majority`

### Data Preparation

For optimal performance and functionality, consider the following:

1. **Create Text Indexes** for collections you want to search by text:

```javascript
// In MongoDB shell or MongoDB Compass
db.your_collection.createIndex({ "field_to_search": "text" })

// For multiple fields
db.your_collection.createIndex({ 
  "title": "text", 
  "description": "text", 
  "tags": "text" 
})
```

2. **Ensure Proper Data Types** in your collections for better query results.

3. **Add Descriptive Field Names** to help the AI understand your data structure.

## Starting the Application

1. **Start the Backend Server**:

```bash
cd LangchainBackend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the Frontend Development Server**:

```bash
cd ClientFrontend
npm run serve
```

3. **Access the Application**:
   Open your browser and navigate to the frontend URL (usually http://localhost:8080)

## Using the MongoDB Integration

### UI Interface

The chatbot interface includes a "🗃️ DB" button in the top right corner. Clicking this button will automatically ask the chatbot to show available collections in the database.

### Example Queries

The chatbot can now answer questions about your MongoDB database. Here are some example queries you can try:

#### Basic Collection Information
- "What collections are available in the database?"
- "How many collections are in the database?"
- "What kind of data is stored in the [collection_name] collection?"

#### Querying Documents
- "Show me the first 5 documents in the [collection_name] collection"
- "Get 10 documents from the [collection_name] collection"
- "Show me documents from [collection_name] starting from the 20th document"

#### Searching and Filtering
- "Search for documents in [collection_name] that contain [search_term]"
- "Find documents in [collection_name] where [field] equals [value]"
- "Find products with price greater than 100"
- "Search for users with email containing 'gmail.com'"

#### Data Analysis
- "What is the structure of documents in the [collection_name] collection?"
- "Show me a summary of the [collection_name] collection"
- "What fields are available in the [collection_name] collection?"

## How It Works

The MongoDB integration uses LangChain tools to interact with MongoDB. The system flow is:

1. **Query Detection**: The backend detects database-related keywords in your query
2. **Agent Routing**: Your query is routed to the LangChain agent with MongoDB tools
3. **Tool Selection**: The agent determines which MongoDB operation to perform
4. **Query Execution**: The operation is executed against your MongoDB database
5. **Result Formatting**: Results are formatted and returned to the frontend
6. **Display**: The chatbot displays the results in a conversational format

### Available MongoDB Tools

The integration includes several tools for interacting with MongoDB:

1. **list_mongodb_collections**: Lists all collections in the database
2. **query_mongodb_collection**: Queries a collection with optional filtering
3. **get_mongodb_document**: Gets a specific document by its ID
4. **search_mongodb_text**: Performs text search across a collection

## Troubleshooting

### Connection Issues

- **Error**: "Failed to connect to MongoDB"
  - Verify your MongoDB connection string in the .env file
  - Ensure MongoDB is running and accessible from the server
  - Check network permissions and firewall settings
  - Verify that the MongoDB user has appropriate permissions

- **Error**: "Authentication failed"
  - Check username and password in your connection string
  - Verify that the user exists in the authentication database

### Query Issues

- **Error**: "Collection not found"
  - Verify that the collection exists in your database
  - Check for typos in collection names

- **Error**: "Text search failed"
  - Ensure text indexes are created on relevant fields
  - Check that the search term is valid

- **No Results**: 
  - Verify that your collection contains data
  - Check that your query criteria match the data structure

### Performance Issues

- **Slow Responses**:
  - Large result sets may cause slow responses
  - Add appropriate indexes to your collections
  - Limit the number of results returned using the limit parameter
  - Consider using projection to return only necessary fields

## Advanced Configuration

### Customizing MongoDB Tools

You can modify the MongoDB tools in `LangchainBackend/app/mongodb_tools.py` to:

1. **Add Custom Tools** for specific database operations:

```python
class CustomAggregationTool(BaseTool):
    """Tool for running aggregation pipelines."""
    name = "run_mongodb_aggregation"
    description = "Runs an aggregation pipeline on a MongoDB collection"
    
    def _run(self, collection_name: str, pipeline: str) -> str:
        # Implementation here
        pass
```

2. **Modify Existing Tools** to change their behavior or add features.

3. **Adjust Query Detection** in `LangchainBackend/app/main.py`:

```python
# Add or modify keywords for database query detection
if any(keyword in chat_message.message.lower() for keyword in 
       ["database", "mongodb", "collection", "data", "query", "find", 
        "search", "document", "record", "field", "aggregate"]):
    # Use the agent with tools
    response = agent.run(chat_message.message)
```

### Security Considerations

1. **Read-Only Access**: Configure your MongoDB user with read-only permissions to prevent data modification.

2. **Connection String Security**: Store your MongoDB connection string securely and never expose it in client-side code.

3. **Query Limitations**: Consider adding limits to the number of documents that can be returned to prevent excessive data transfer.

4. **Input Validation**: The system performs basic validation, but consider adding additional validation for production use.

## Example Use Cases

1. **Customer Support**: Allow support agents to query customer data through natural language.

2. **Data Analysis**: Enable non-technical users to explore and analyze data in MongoDB.

3. **Content Management**: Query and retrieve content from a MongoDB-based CMS.

4. **Inventory Management**: Check product availability and details through conversational queries.

## Further Enhancements

1. **Result Visualization**: Add charts or tables for visualizing query results.

2. **Query History**: Save and reuse previous database queries.

3. **Advanced Filtering**: Implement more complex query capabilities.

4. **Write Operations**: Add secure methods for data insertion or updates.

5. **Streaming Responses**: Implement streaming for large result sets.

---

For more information, refer to the [MongoDB Documentation](https://docs.mongodb.com/) and [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction). 