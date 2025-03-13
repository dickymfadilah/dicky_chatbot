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

# Create a custom prompt template for the conversation chain
conversation_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=f"{SYSTEM_PROMPT}\n\nConversation History:\n{{history}}\nHuman: {{input}}\nAI:"
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
        max_iterations=5,  # Limit iterations to prevent infinite loops
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
        2. If yes, which collection might it be referring to?
        3. What type of query is needed? (list collections, query documents, get document by id, text search)
        
        User message: "{chat_message.message}"
        
        Provide your analysis in VALID JSON format with the following structure:
        {{
            "is_database_question": true/false,
            "collection": "collection_name_or_null",
            "query_type": "list_collections/query_documents/get_document/text_search"
        }}
        
        DO NOT include comments, explanations, or any non-JSON content in your response.
        Ensure all property names are in double quotes and follow standard JSON format.
        """
        
        analysis_response = llm.invoke(analysis_prompt)
        
        # Extract JSON from the response if possible
        try:
            # Try to find JSON-like content in the response
            json_match = re.search(r'\{.*\}', analysis_response, re.DOTALL)
            if json_match:
                # Clean up the JSON string to remove comments and ensure valid format
                json_str = json_match.group(0)
                # Remove any comments (// comment or /* comment */)
                json_str = re.sub(r'//.*?(\n|$)|/\*.*?\*/', '', json_str, flags=re.DOTALL)
                # Replace single quotes with double quotes for JSON compliance
                json_str = json_str.replace("'", '"')
                # Ensure boolean values are lowercase
                json_str = json_str.replace("True", "true").replace("False", "false")
                
                try:
                    analysis_json = json.loads(json_str)
                except json.JSONDecodeError:
                    # If still invalid, try a more aggressive cleanup
                    # Extract just the key-value pairs
                    pairs = re.findall(r'"([^"]+)"\s*:\s*("[^"]*"|true|false|\d+|null)', json_str)
                    if pairs:
                        clean_json = '{' + ','.join([f'"{k}": {v}' for k, v in pairs]) + '}'
                        analysis_json = json.loads(clean_json)
                    else:
                        raise
            else:
                # Fallback: create a simple analysis based on keywords
                is_db_query = any(keyword in chat_message.message.lower() for keyword in 
                    ["database", "mongodb", "collection", "data", "query", "find", "search", "list"])
                analysis_json = {
                    "is_database_question": is_db_query,
                    "collection": None,
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
        
        # Normalize the JSON keys to handle variations in key names
        normalized_json = {}
        for key, value in analysis_json.items():
            # Convert keys to lowercase for case-insensitive matching
            key_lower = key.lower()
            if any(db_key in key_lower for db_key in ["database", "db", "is_database"]):
                normalized_json["is_database_question"] = (
                    value if isinstance(value, bool) 
                    else isinstance(value, str) and value.lower() in ["yes", "true", "1"]
                )
            elif "collection" in key_lower:
                normalized_json["collection"] = value
            elif "query" in key_lower or "type" in key_lower:
                normalized_json["query_type"] = value
        
        # Ensure all required keys exist
        if "is_database_question" not in normalized_json:
            normalized_json["is_database_question"] = False
        if "collection" not in normalized_json:
            normalized_json["collection"] = None
        if "query_type" not in normalized_json:
            normalized_json["query_type"] = "query_documents"
        
        # Handle database-related questions
        if normalized_json.get("is_database_question", False):
            # If we have a functioning agent, use it
            if agent is not None:
                try:
                    response = agent.run(input=chat_message.message)
                    return ChatResponse(response=response)
                except Exception as agent_error:
                    print(f"Agent error: {str(agent_error)}")
            
            # If agent fails or is not available, use direct handling
            try:
                from .mongodb_utils import get_mongodb_client
                client = get_mongodb_client()
                
                # Get the collection name from analysis or try to extract it
                collection_name = normalized_json.get("collection")
                if not collection_name or collection_name == "null":
                    # Try to extract collection name from the query
                    words = chat_message.message.lower().split()
                    for i, word in enumerate(words):
                        if word in ["collection", "collections"] and i+1 < len(words):
                            collection_name = words[i+1]
                            break
                
                # Handle different query types
                query_type = normalized_json.get("query_type", "query_documents")
                
                # List collections
                if query_type == "list_collections" or "list" in chat_message.message.lower() and "collection" in chat_message.message.lower():
                    collections = client.get_collections()
                    return ChatResponse(response=f"Available collections: {', '.join(collections)}")
                
                # Query a specific collection
                elif collection_name and collection_name != "null":
                    try:
                        # Default to showing some data from the collection
                        data = client.query_collection(collection_name, None, 5, 0)
                        return ChatResponse(response=f"Here's some data from the '{collection_name}' collection:\n{json.dumps(data, indent=2, default=str)}")
                    except Exception as collection_error:
                        print(f"Collection query error: {str(collection_error)}")
                        collections = client.get_collections()
                        return ChatResponse(response=f"I couldn't find or query the collection '{collection_name}'. Available collections are: {', '.join(collections)}")
                
                # Fallback to listing collections
                else:
                    collections = client.get_collections()
                    return ChatResponse(response=f"I'm not sure which collection you're interested in. Here are the available collections: {', '.join(collections)}")
                    
            except Exception as direct_error:
                print(f"Direct handling error: {str(direct_error)}")
                # Final fallback to conversation
                response = conversation.predict(input=f"I couldn't access the database information you requested. Could you please clarify what you're looking for? Available commands include: list collections, show collection [name], etc.")
                return ChatResponse(response=response)
        
        # For non-database questions, use the regular conversation chain
        response = conversation.predict(input=chat_message.message)
        return ChatResponse(response=response)
        
    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        # Return a more user-friendly error message
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