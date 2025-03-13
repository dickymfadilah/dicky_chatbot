from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import json
import re

from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate

# Import MongoDB tools
from .mongodb_tools import get_mongodb_tools

# Load environment variables
load_dotenv()

app = FastAPI(title="LangChain Ollama Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Ollama LLM
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model_name = os.getenv("MODEL_NAME", "llama3")

llm = Ollama(
    model=model_name,
    base_url=ollama_base_url,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

# Initialize conversation memory
memory = ConversationBufferMemory(return_messages=True)

# Get MongoDB tools
mongodb_tools = get_mongodb_tools()

# Define system prompt for better query understanding
SYSTEM_PROMPT = """You are an intelligent assistant with access to a MongoDB database.
Your task is to understand user queries and determine whether they are:
1. General questions that can be answered directly
2. Database-related questions that require querying MongoDB

For database-related questions, you should:
- Identify which collection the user is interested in
- Determine what kind of data they want to retrieve
- Formulate an appropriate query to get that data

Available MongoDB collections can be accessed using the tools provided.
Available operations include:
- Listing all collections
- Querying documents from a collection with filters
- Getting a specific document by ID
- Performing text search across a collection

Think step by step to determine the best way to respond to the user's query.
"""

# Define data analysis prompt for analyzing database results
DATA_ANALYSIS_PROMPT = """You are a data analysis expert. You have been provided with data from a MongoDB database.
Your task is to analyze this data and provide insights based on the user's question.

The data has been retrieved from the database based on the user's query. Now you need to:
1. Understand what the user is asking about this data
2. Analyze the provided data to find relevant information
3. Present your findings in a clear, concise manner
4. If appropriate, suggest further queries or analyses that might be helpful

Remember to focus on the specific aspects of the data that the user is interested in.
"""

# Create a custom prompt template for the conversation chain
conversation_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=f"{SYSTEM_PROMPT}\n\nConversation History:\n{{history}}\nHuman: {{input}}\nAI:"
)

# Create a data analysis prompt template
data_analysis_prompt = PromptTemplate(
    input_variables=["data", "question"],
    template=f"{DATA_ANALYSIS_PROMPT}\n\nUser Question: {{question}}\n\nDatabase Data: {{data}}\n\nAnalysis:"
)

# Initialize a regular conversation chain with the custom prompt
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=conversation_prompt,
    verbose=True
)

# Initialize agent with tools and system prompt
try:
    agent = initialize_agent(
        tools=mongodb_tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=3,  # Reduce max iterations to prevent loops
        max_execution_time=10.0,  # Add timeout to prevent long-running operations
        system_message=SYSTEM_PROMPT
    )
except Exception as e:
    print(f"Error initializing agent: {str(e)}")
    agent = None

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    
class ChatHistory(BaseModel):
    history: List[dict]

@app.get("/")
async def root():
    return {"message": "Welcome to the LangChain Ollama Chatbot API"}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        # First, analyze the user's message to determine intent
        analysis_prompt = f"""
        Analyze the following user message and determine:
        1. Is this a database-related question? (yes/no)
        2. If yes, which collection might it be referring to? (If collection name doesn't end with 's', add 's')
        3. What type of query is needed? (list collections, query documents, get document by id, text search)
        
        IMPORTANT NOTES ABOUT MONGODB COLLECTIONS:
        - MongoDB collection names typically end with 's' (e.g., users, products, orders, transactions)
        - Collections store multiple related documents of the same type
        - Look for plural nouns in the user's message as they likely refer to collections
        - Common collection naming patterns: 
          * Plural nouns (users, products, orders)
          * Entity + action (userLogins, productViews)
          * Domain-specific terms (transactions, analytics, metrics)
        
        User message: "{chat_message.message}"
        
        Provide your analysis in VALID JSON format with the following structure:
        {{
            "is_database_question": true/false,
            "collection": "collection_name_or_null",
            "query_type": "list_collections/query_documents/get_document/text_search"
        }}
                
        DO NOT include comments, explanations, or any non-JSON content in your response.
        Ensure all property names are in double quotes and follow standard JSON format.
        If you detect a potential collection name that doesn't end with 's', add 's' to make it plural.
        """
        
        analysis_response = llm.invoke(analysis_prompt)
        
        # Extract JSON from the response if possible
        try:
            # Try to find JSON-like content in the response
            json_match = re.search(r'\{.*\}', analysis_response, re.DOTALL)
            if json_match:
                # Clean up the JSON string to remove comments and ensure valid format
                json_str = json_match.group(0)
                # Replace single quotes with double quotes for JSON compliance
                json_str = json_str.replace("'", '"')
                # Ensure boolean values are lowercase
                json_str = json_str.replace("True", "true").replace("False", "false")
                
                analysis_json = json.loads(json_str)
            else:
                # Fallback: create a simple analysis based on keywords
                is_db_query = any(keyword in chat_message.message.lower() for keyword in 
                    ["database", "mongodb", "collection", "data", "query", "find", "search", "list"])
                
                # Try to extract collection name from the message
                collection_name = None
                words = chat_message.message.lower().split()
                for i, word in enumerate(words):
                    # Look for nouns that might be collections
                    if len(word) > 3 and i > 0:  # Skip short words and first word
                        # Check if it's a potential collection name (not a common verb or preposition)
                        if word not in ["from", "where", "what", "when", "how", "show", "get", "find", "query"]:
                            # Make sure it ends with 's'
                            if not word.endswith('s'):
                                word = word + 's'
                            collection_name = word
                            break
                
                analysis_json = {
                    "is_database_question": is_db_query,
                    "collection": collection_name,
                    "query_type": "list_collections" if "list" in chat_message.message.lower() else "query_documents"
                }
        except Exception as json_error:
            print(f"Error parsing analysis JSON: {str(json_error)}")
            # Fallback analysis
            is_db_query = any(keyword in chat_message.message.lower() for keyword in 
                ["database", "mongodb", "collection", "data", "query", "find", "search", "list"])
            analysis_json = {
                "is_database_question": is_db_query,
                "collection": None,
                "query_type": "list_collections" if "list" in chat_message.message.lower() else "query_documents"
            }
        
        print(f"Analysis result: {analysis_json}")
        
        # Handle database-related questions with the agent
        if analysis_json.get("is_database_question", False) and agent is not None:
            print("Database-related question detected")
            try:
                # Get collection information
                collection_name = analysis_json.get("collection")
                query_type = analysis_json.get("query_type", "query_documents")
                
                # Get data from the database
                db_data = None
                
                try:
                    from .mongodb_utils import get_mongodb_client
                    client = get_mongodb_client()
                    
                    # Get list of collections for reference
                    collection_list = client.get_collections()
                    
                    # List collections
                    if query_type == "list_collections" or not collection_name:
                        db_data = {"collections": collection_list}
                    
                    # Query a specific collection
                    elif collection_name and collection_name in collection_list:
                        data = client.query_collection(collection_name, None, 10, 0)
                        db_data = {"collection": collection_name, "data": data}
                    
                except Exception as db_error:
                    print(f"Database access error: {str(db_error)}")
                    db_data = {"error": "Could not access database"}
                
                # If we have database data, include it in the agent's context
                if db_data:
                    # Format the data for the agent
                    data_str = json.dumps(db_data, indent=2, default=str)
                    enhanced_query = f"""
                    User query: {chat_message.message}
                    
                    Database information: {data_str}
                    
                    Please analyze this data and answer the user's question.
                    """
                    
                    # Use the agent with the enhanced query
                    agent_response = agent.run(enhanced_query)
                else:
                    # Use the agent with the original query if no data was retrieved
                    agent_response = agent.run(chat_message.message)
                
                return ChatResponse(response=agent_response)
            except Exception as agent_error:
                print(f"Agent error: {str(agent_error)}")
                return ChatResponse(response="I encountered an error while trying to query the database. Please try a different question.")
        else:
            # For non-database questions, use the conversation chain directly
            response = conversation.predict(input=chat_message.message)
            return ChatResponse(response=response)
        
    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        return ChatResponse(response="I'm sorry, I encountered an error processing your request. Please try again with a different question.")

@app.get("/history", response_model=ChatHistory)
async def get_history():
    try:
        # Get conversation history from memory
        history = memory.chat_memory.messages
        formatted_history = [{"role": msg.type, "content": msg.content} for msg in history]
        return ChatHistory(history=formatted_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history")
async def clear_history():
    try:
        # Clear conversation memory
        memory.clear()
        return {"message": "Conversation history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def get_collections():
    try:
        from .mongodb_utils import get_mongodb_client
        client = get_mongodb_client()
        collections = client.get_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collection/{collection_name}")
async def get_collection_data(collection_name: str, limit: int = 10, skip: int = 0):
    try:
        from .mongodb_utils import get_mongodb_client
        client = get_mongodb_client()
        data = client.query_collection(collection_name, None, limit, skip)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 