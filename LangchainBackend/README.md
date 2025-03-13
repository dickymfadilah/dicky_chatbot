# LangChain Ollama Chatbot Backend

This is the backend component of the LangChain Ollama Chatbot application.

## Overview

The backend is built with FastAPI and uses LangChain to integrate with Ollama's Llama 3 model. It provides a RESTful API for the frontend to communicate with the AI model.

## Features

- FastAPI web server with CORS support
- LangChain integration with Ollama
- Conversation memory management
- Simple API for chat interactions

## Chatbot Capabilities

The Llama 3 model through Ollama can:

### Knowledge and Information

- Answer general knowledge questions
- Provide explanations of concepts
- Discuss historical events and figures
- Explain scientific principles
- Offer definitions and clarifications

### Language Tasks

- Assist with writing and composition
- Suggest synonyms and alternative phrasings
- Help with grammar and language usage
- Generate creative content like stories or poems
- Summarize information

### Reasoning

- Perform simple logical reasoning
- Work through basic problems step by step
- Provide explanations for concepts
- Offer opinions based on provided information

### Limitations

- Cannot access real-time information or the internet
- Knowledge is limited to the model's training data
- Cannot execute code or perform complex calculations
- No access to personal data unless explicitly provided in the conversation

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure Ollama is installed and running with the Llama 3 model:
   ```
   ollama pull llama3
   ```

3. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

## API Endpoints

- `GET /`: Welcome message
- `POST /chat`: Send a message to the chatbot
  - Request body: `{"message": "Your message here"}`
  - Response: `{"response": "AI response here"}`
- `GET /history`: Get conversation history
- `DELETE /history`: Clear conversation history

## Environment Variables

Create a `.env` file with the following variables:
- `OLLAMA_BASE_URL`: URL for the Ollama API (default: http://localhost:11434)
- `MODEL_NAME`: The model to use with Ollama (default: llama3)

## Example Usage

```python
import requests

# Send a message to the chatbot
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What is artificial intelligence?"}
)
print(response.json())

# Get conversation history
history = requests.get("http://localhost:8000/history")
print(history.json())

# Clear conversation history
clear = requests.delete("http://localhost:8000/history")
print(clear.json())
``` 