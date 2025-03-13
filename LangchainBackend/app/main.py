from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import json

from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

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

# Initialize a regular conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Initialize agent with tools - using a try-except block to handle initialization errors
try:
    agent = initialize_agent(
        tools=mongodb_tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=5  # Limit iterations to prevent infinite loops
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
        # Parse the user's message to identify database-related queries
        message = chat_message.message.lower()
        
        # Direct handling of common database queries without using the agent
        if "list" in message and "collection" in message:
            try:
                from .mongodb_utils import get_mongodb_client
                client = get_mongodb_client()
                collections = client.get_collections()
                return ChatResponse(response=f"Available collections: {', '.join(collections)}")
            except Exception as e:
                print(f"Direct collection listing error: {str(e)}")
        
        # Check if the message is asking for collection data
        collection_query_match = None
        if "collection" in message and any(word in message for word in ["show", "get", "list", "query", "find"]):
            words = message.split()
            for i, word in enumerate(words):
                if word == "collection" and i+1 < len(words):
                    collection_query_match = words[i+1]
                    break
            
            if collection_query_match:
                try:
                    from .mongodb_utils import get_mongodb_client
                    client = get_mongodb_client()
                    data = client.query_collection(collection_query_match, None, 10, 0)
                    return ChatResponse(response=f"Data from collection '{collection_query_match}':\n{json.dumps(data, indent=2, default=str)}")
                except Exception as e:
                    print(f"Direct collection query error: {str(e)}")
        
        # General database query detection
        is_db_query = any(keyword in message for keyword in 
               ["database", "mongodb", "collection", "data", "query", "find", "search"])
        
        if is_db_query and agent is not None:
            try:
                # Use the agent with tools
                response = agent.run(chat_message.message)
                return ChatResponse(response=response)
            except Exception as agent_error:
                print(f"Agent error: {str(agent_error)}")
                # Try direct handling if agent fails
                try:
                    from .mongodb_utils import get_mongodb_client
                    client = get_mongodb_client()
                    
                    # Try to extract collection name from the query
                    words = message.split()
                    collection_name = None
                    for i, word in enumerate(words):
                        if word in ["collection", "collections"] and i+1 < len(words):
                            collection_name = words[i+1]
                            break
                    
                    if collection_name:
                        # Try to get data from the collection
                        try:
                            data = client.query_collection(collection_name, None, 5, 0)
                            return ChatResponse(response=f"Here's some data from the '{collection_name}' collection:\n{json.dumps(data[:5], indent=2, default=str)}")
                        except Exception:
                            pass
                    
                    # Fallback to listing collections
                    collections = client.get_collections()
                    return ChatResponse(response=f"I'm not sure what specific database information you're looking for. Here are the available collections: {', '.join(collections)}")
                except Exception as direct_error:
                    print(f"Direct handling error: {str(direct_error)}")
                    # Final fallback to conversation
                    response = conversation.predict(input=f"I couldn't access the database information you requested. Could you please clarify what you're looking for? Available commands include: list collections, show collection [name], etc.")
                    return ChatResponse(response=response)
        
        # Use the regular conversation chain for non-database queries
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