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

Available MongoDB collections can be accessed using the tools provided.
Available operations include:
- Listing all collections
- Querying documents from a collection with filters
- Getting a specific document by ID
- Performing text search across a collection

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
                return {"collection": collection_name, "data": data}
            
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