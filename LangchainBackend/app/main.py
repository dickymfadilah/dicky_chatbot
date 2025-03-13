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

# Initialize agent with tools
agent = initialize_agent(
    tools=mongodb_tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True
)

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
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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