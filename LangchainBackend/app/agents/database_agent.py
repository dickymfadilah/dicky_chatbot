from typing import Dict, Any, List, Optional
import json

from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool

from ..mongodb_utils import get_mongodb_client

class DatabaseAgent:
    """
    Agent responsible for handling database-related questions using MongoDB tools.
    """
    
    def __init__(self, llm: Ollama, mongodb_tools: List[Tool], memory: ConversationBufferMemory = None):
        """
        Initialize the database agent.
        
        Args:
            llm: The language model to use for database interactions
            mongodb_tools: List of MongoDB tools for the agent to use
            memory: Optional conversation memory to maintain context
        """
        self.llm = llm
        self.mongodb_tools = mongodb_tools
        self.memory = memory if memory else ConversationBufferMemory(return_messages=True)
        
        # Define system prompt for database questions
        self.system_prompt = """Hi! I'm Octopus, an AI assistant created by DQ to help with database questions.
Your task is to help users retrieve and understand data from the database.

For database-related questions, you should:
- Identify which collection the user is interested in
- Determine what kind of data they want to retrieve
- Formulate an appropriate query to get that data
- Present the results in a clear, understandable format
- When asked about schema or structure, analyze and describe the keys and data types in the collection

IMPORTANT DISTINCTION:
- When users ask to "list collections" or "show collections", provide a simple list of available collections
- When users ask about "schema", "structure", "fields", "keys", or "data types" of a collection, provide detailed schema information for that specific collection, NOT just a list of collections

When showing collection schema details:
- List all fields/keys present in the collection documents
- Identify the data type of each field (string, number, boolean, array, object, etc.)
- Describe nested structures if present
- Highlight required vs optional fields if determinable
- Provide examples of data formats for complex fields
- Format the schema information in a clear, structured way (tables or bullet points)

Available MongoDB collections can be accessed using the tools provided.
Available operations include:
- Listing all collections
- Querying documents from a collection with filters
- Getting a specific document by ID
- Performing text search across a collection
- Analyzing collection schema and structure

Think step by step to determine the best way to respond to the user's query.
"""
        
        # Initialize agent with tools and system prompt
        try:
            self.agent = initialize_agent(
                tools=mongodb_tools,
                llm=llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=True,
                memory=self.memory,
                handle_parsing_errors=True,
                max_iterations=3,  # Reduce max iterations to prevent loops
                max_execution_time=10.0,  # Add timeout to prevent long-running operations
                system_message=self.system_prompt
            )
        except Exception as e:
            print(f"Error initializing database agent: {str(e)}")
            self.agent = None
    
    def query_database(self, user_message: str, collection_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the database based on the user's message and collection information.
        
        Args:
            user_message: The user's message/question
            collection_info: Dictionary with collection information:
                {
                    "collection": str or None,
                    "query_type": str
                }
                
        Returns:
            Dictionary with database data or error information
        """
        try:
            # Extract collection information
            collection_name = collection_info.get("collection")
            query_type = collection_info.get("query_type", "query_documents")
            
            # Check if this is a schema-related query
            is_schema_query = any(term in user_message.lower() for term in ["schema", "structure", "fields", "keys", "data types", "format"])
            
            # Get data from the database
            client = get_mongodb_client()
            
            # Get list of collections for reference
            collection_list = client.get_collections()
            
            # List collections
            if query_type == "list_collections" or not collection_name:
                return {"collections": collection_list}
            
            # Query a specific collection
            elif collection_name and collection_name in collection_list:
                data = client.query_collection(collection_name, None, 10, 0)
                result = {"collection": collection_name, "data": data}
                
                # Always extract schema information for specific collection queries
                # This ensures schema data is available even if not explicitly requested
                if data:
                    schema_info = self._extract_schema_from_documents(data)
                    result["schema"] = schema_info
                    
                    # If this is specifically a schema query, add a flag to indicate that
                    if is_schema_query:
                        result["is_schema_query"] = True
                
                return result
            
            # Collection not found
            elif collection_name:
                return {
                    "error": f"Collection '{collection_name}' not found",
                    "available_collections": collection_list
                }
            
            # Fallback
            return {"collections": collection_list}
            
        except Exception as db_error:
            print(f"Database access error: {str(db_error)}")
            return {"error": "Could not access database"}
    
    def _extract_schema_from_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract schema information from a list of documents.
        
        Args:
            documents: List of MongoDB documents
            
        Returns:
            Dictionary with schema information
        """
        if not documents:
            return {"message": "No documents available to extract schema"}
        
        schema = {}
        
        # Process each document to build a comprehensive schema
        for doc in documents:
            self._process_document_for_schema(doc, schema)
        
        # Add occurrence counts to determine if fields are required or optional
        total_docs = len(documents)
        for field, info in schema.items():
            if "count" in info:
                info["occurrence_rate"] = f"{(info['count'] / total_docs) * 100:.1f}%"
                if info["count"] == total_docs:
                    info["required"] = True
                else:
                    info["required"] = False
        
        # Add metadata to the schema
        schema_metadata = {
            "total_documents": total_docs,
            "top_level_fields": [field for field in schema.keys() if "." not in field and "[]" not in field],
            "has_nested_fields": any("." in field for field in schema.keys()),
            "has_array_fields": any("[]" in field for field in schema.keys())
        }
        
        # Return enhanced schema with metadata
        return {
            "metadata": schema_metadata,
            "fields": schema
        }
    
    def _process_document_for_schema(self, doc: Dict[str, Any], schema: Dict[str, Any], prefix: str = ""):
        """
        Process a document to extract schema information.
        
        Args:
            doc: MongoDB document
            schema: Schema dictionary to update
            prefix: Prefix for nested fields
        """
        for key, value in doc.items():
            field_name = f"{prefix}{key}"
            
            # Initialize field in schema if not exists
            if field_name not in schema:
                schema[field_name] = {
                    "type": self._get_type_name(value),
                    "count": 1,
                    "example": str(value)[:100] if value is not None else None  # Truncate long examples
                }
            else:
                schema[field_name]["count"] += 1
                
                # Update type if it's a union type
                current_type = schema[field_name]["type"]
                new_type = self._get_type_name(value)
                if current_type != new_type:
                    schema[field_name]["type"] = f"{current_type} | {new_type}"
            
            # Process nested objects
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    nested_field = f"{field_name}.{nested_key}"
                    if nested_field not in schema:
                        schema[nested_field] = {
                            "type": self._get_type_name(nested_value),
                            "count": 1,
                            "example": str(nested_value)[:100] if nested_value is not None else None
                        }
                    else:
                        schema[nested_field]["count"] += 1
            
            # Process arrays with objects
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                schema[field_name]["array_items"] = "object"
                # Process the first item as an example
                if value:
                    for nested_key, nested_value in value[0].items():
                        nested_field = f"{field_name}[].{nested_key}"
                        if nested_field not in schema:
                            schema[nested_field] = {
                                "type": self._get_type_name(nested_value),
                                "count": 1,
                                "example": str(nested_value)[:100] if nested_value is not None else None
                            }
                        else:
                            schema[nested_field]["count"] += 1
    
    def _get_type_name(self, value: Any) -> str:
        """
        Get the type name of a value.
        
        Args:
            value: Any value
            
        Returns:
            String representation of the type
        """
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            if not value:
                return "array"
            item_type = self._get_type_name(value[0])
            return f"array<{item_type}>"
        elif isinstance(value, dict):
            return "object"
        else:
            return type(value).__name__
    
    def process_query(self, user_message: str, collection_info: Dict[str, Any]) -> str:
        """
        Process a database query and return a response.
        
        Args:
            user_message: The user's message/question
            collection_info: Dictionary with collection information
            
        Returns:
            The agent's response
        """
        if self.agent is None:
            return "I'm sorry, the database agent is not available. Please try a different question."
        
        try:
            # Get data from the database
            db_data = self.query_database(user_message, collection_info)
            
            # If we have database data, include it in the agent's context
            if db_data:
                print(f"Database data: {db_data}")
                # Format the data for the agent
                data_str = json.dumps(db_data, indent=2, default=str)
                
                # Check if this is a schema-related query
                is_schema_query = any(term in user_message.lower() for term in ["schema", "structure", "fields", "keys", "data types", "format"])
                is_list_collections_query = any(term in user_message.lower() for term in ["list collections", "show collections", "what collections"])
                
                # Determine if we're dealing with a specific collection
                has_specific_collection = "collection" in db_data and "data" in db_data
                
                if is_schema_query and has_specific_collection:
                    collection_name = db_data.get("collection", "")
                    enhanced_query = f"""
                    User query: {user_message}
                    
                    Database information: {data_str}
                    
                    This is a schema-related query for the '{collection_name}' collection. Please analyze the schema information provided and:
                    1. List all fields/keys in the collection
                    2. Show the data type of each field
                    3. Indicate which fields are required vs optional (based on occurrence rate)
                    4. Describe any nested structures
                    5. Provide examples of data formats where helpful
                    
                    Format your response in a clear, structured way using tables or bullet points.
                    DO NOT just list the collections - the user wants detailed schema information about the '{collection_name}' collection.
                    """
                elif is_schema_query and not has_specific_collection:
                    enhanced_query = f"""
                    User query: {user_message}
                    
                    Database information: {data_str}
                    
                    The user is asking about schema information, but we need a specific collection to analyze.
                    Please inform the user that they need to specify which collection they want to see the schema for.
                    List the available collections and ask them to choose one for schema analysis.
                    """
                elif is_list_collections_query:
                    enhanced_query = f"""
                    User query: {user_message}
                    
                    Database information: {data_str}
                    
                    The user wants to list the available collections. Please provide a simple list of all collections in the database.
                    """
                else:
                    enhanced_query = f"""
                    User query: {user_message}
                    
                    Database information: {data_str}
                    
                    Please analyze this data and answer the user's question.
                    """
                
                # Use the agent with the enhanced query
                agent_response = self.agent.invoke({
                    "input": enhanced_query,
                    "chat_history": self.memory.chat_memory.messages
                })
                # Extract the response from the agent's output
                if isinstance(agent_response, dict) and "output" in agent_response:
                    agent_response = agent_response["output"]
            else:
                # Use the agent with the original query if no data was retrieved
                agent_response = self.agent.invoke({
                    "input": user_message,
                    "chat_history": self.memory.chat_memory.messages
                })
                # Extract the response from the agent's output
                if isinstance(agent_response, dict) and "output" in agent_response:
                    agent_response = agent_response["output"]
            
            return agent_response
            
        except Exception as agent_error:
            print(f"Agent error: {str(agent_error)}")
            return "I encountered an error while trying to query the database. Please try a different question." 