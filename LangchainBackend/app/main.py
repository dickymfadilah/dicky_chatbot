from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

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
llm = Ollama(model="llama3")

# Initialize conversation memory
memory = ConversationBufferMemory()

# Initialize conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
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
        # Get response from LLM
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 