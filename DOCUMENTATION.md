# LangChain Ollama Chatbot Documentation

## Project Overview

This project implements a chatbot application using LangChain with Ollama for the backend and Vue.js for the frontend. The application allows users to interact with an AI assistant powered by Ollama's language models.

## Architecture

The project is divided into two main components:

1. **LangchainBackend**: A Python-based backend using FastAPI and LangChain
2. **ClientFrontend**: A Vue.js frontend application

### Backend Architecture

The backend is built with FastAPI and uses LangChain to integrate with Ollama. The main components are:

- **FastAPI Application**: Provides REST API endpoints for the frontend
- **LangChain Integration**: Uses LangChain to interact with Ollama's language models
- **Conversation Memory**: Manages and persists conversation history
- **CORS Middleware**: Enables cross-origin requests from the frontend

### Frontend Architecture

The frontend is built with Vue.js 3 and uses Vuex for state management. The main components are:

- **Vue Router**: Manages navigation within the application
- **Vuex Store**: Manages application state and API communication
- **Chat Interface**: Provides a user-friendly interface for interacting with the AI
- **Responsive Design**: Ensures the application works well on different devices

## API Reference

### Backend API Endpoints

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/` | GET | Welcome message | None | `{"message": "Welcome to the LangChain Ollama Chatbot API"}` |
| `/chat` | POST | Send a message to the chatbot | `{"message": "Your message"}` | `{"response": "AI response"}` |
| `/history` | GET | Get conversation history | None | `{"history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}` |
| `/history` | DELETE | Clear conversation history | None | `{"message": "Conversation history cleared successfully"}` |

## Data Flow

1. User sends a message through the frontend interface
2. Frontend sends a POST request to the `/chat` endpoint
3. Backend processes the message using LangChain and Ollama
4. Backend returns the AI response
5. Frontend displays the response to the user
6. Conversation history is stored in memory on the backend
7. Frontend can retrieve or clear the conversation history as needed

## Configuration

### Backend Configuration

The backend can be configured using environment variables in the `.env` file:

- `OLLAMA_BASE_URL`: URL for the Ollama API (default: http://localhost:11434)
- `MODEL_NAME`: The model to use with Ollama (default: llama3)

### Frontend Configuration

The frontend can be configured using environment variables in the `.env` file:

- `VUE_APP_API_URL`: URL for the backend API (default: http://localhost:8000)

## Security Considerations

- The current implementation uses CORS with `allow_origins=["*"]`, which should be restricted to specific origins in production
- No authentication is implemented in this version
- The application should be deployed behind HTTPS in production

## Performance Considerations

- The backend uses a single instance of the Ollama model, which may limit throughput
- Conversation history is stored in memory, which may cause issues with large conversations or multiple users
- For production use, consider implementing a database for conversation storage

## Error Handling

- The backend includes try-catch blocks to handle exceptions
- The frontend displays error messages to the user when API requests fail
- Both components include logging for debugging purposes

## Future Improvements

- Add user authentication
- Implement database storage for conversation history
- Add support for multiple language models
- Improve error handling and recovery
- Add unit and integration tests
- Implement streaming responses for better user experience 