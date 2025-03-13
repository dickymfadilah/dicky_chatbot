# LangChain Ollama Chatbot Backend

This is a FastAPI backend for a chatbot using LangChain with Ollama.

## Prerequisites

- Python 3.9+
- Ollama installed and running locally (https://ollama.ai/)
- Llama3 model pulled in Ollama (`ollama pull llama3`)

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Make sure Ollama is running in the background with the Llama3 model available.

2. Start the FastAPI server:
   ```
   cd app
   uvicorn main:app --reload
   ```

3. The API will be available at http://localhost:8000

## API Endpoints

- `GET /`: Welcome message
- `POST /chat`: Send a message to the chatbot
  - Request body: `{"message": "Your message here"}`
- `GET /history`: Get conversation history
- `DELETE /history`: Clear conversation history

## Environment Variables

You can create a `.env` file in the root directory with the following variables:
- `OLLAMA_BASE_URL`: URL for Ollama API (default: http://localhost:11434)
- `MODEL_NAME`: Model to use (default: llama3) 