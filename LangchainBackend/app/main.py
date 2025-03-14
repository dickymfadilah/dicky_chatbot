from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Import MongoDB tools
from .mongodb_tools import get_mongodb_tools

# Import agents
from .agents import ClassifierAgent, GeneralAgent, DatabaseAgent, AnalysisAgent

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

# Initialize agents
classifier_agent = ClassifierAgent(llm=llm)
general_agent = GeneralAgent(llm=llm, memory=memory)
database_agent = DatabaseAgent(llm=llm, mongodb_tools=mongodb_tools, memory=memory)
analysis_agent = AnalysisAgent(llm=llm)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    
class ChatHistory(BaseModel):
    history: List[Dict[str, Any]]

@app.get("/")
async def root():
    return {"message": "Welcome to the LangChain Ollama Chatbot API"}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        # Step 1: Use the classifier agent to determine if this is a database question
        classification = classifier_agent.classify_query(chat_message.message)
        print(f"Classification result: {classification}")
        
        # Step 2: Route to the appropriate agent based on classification
        if classification.get("is_database_question", False):
            print("Database-related question detected")
            
            # Step 3: Use the database agent to query the database
            db_data = database_agent.query_database(
                chat_message.message, 
                {
                    "collection": classification.get("collection"),
                    "query_type": classification.get("query_type", "query_documents")
                }
            )
            
            # Step 4: Use the analysis agent to analyze the data
            if db_data:
                print(f"Database data retrieved: {db_data}")
                response = analysis_agent.analyze_data(chat_message.message, db_data)
            else:
                # If no data was retrieved, use the database agent directly
                response = database_agent.process_query(
                    chat_message.message,
                    {
                        "collection": classification.get("collection"),
                        "query_type": classification.get("query_type", "query_documents")
                    }
                )
        else:
            # For non-database questions, use the general agent
            print("General question detected")
            response = general_agent.answer_question(chat_message.message)
        
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