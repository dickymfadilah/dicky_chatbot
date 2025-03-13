# LangChain Ollama Chatbot

A modern chatbot application built with LangChain, Ollama, FastAPI, and Vue.js.

![LangChain Ollama Chatbot](https://via.placeholder.com/800x400?text=LangChain+Ollama+Chatbot)

## Overview

This project implements a full-stack chatbot application with the following components:

- **Backend**: Python FastAPI application with LangChain and Ollama integration
- **Frontend**: Vue.js application with Pinia state management and a modern, responsive UI

The chatbot allows users to have natural language conversations with an AI assistant powered by Ollama's Llama 3 model.

## Features

- Real-time chat interface
- Conversation history management
- Clean, modern UI with responsive design
- Easy configuration and deployment
- Cross-platform compatibility

## Chatbot Capabilities

The chatbot can handle a variety of queries and tasks:

### What You Can Ask

- **General Knowledge**: "What is photosynthesis?", "Who wrote Pride and Prejudice?"
- **Conceptual Explanations**: "Explain quantum computing in simple terms"
- **Language Tasks**: "Help me write an email", "Suggest synonyms for 'happy'"
- **Simple Reasoning**: "If I have 5 apples and give away 2, how many do I have left?"
- **Creative Content**: "Write a short poem about nature"

### Limitations

- **Training Cutoff**: The model has a knowledge cutoff date and doesn't know about recent events
- **No Internet Access**: Cannot look up real-time information
- **No Document Knowledge**: Limited to knowledge in its training data
- **No Specialized Tools**: Cannot perform complex calculations or run code

For more detailed information about capabilities, see the [Documentation](DOCUMENTATION.md).

## Project Structure

The project is organized into two main directories:

- **LangchainBackend**: Contains the Python FastAPI backend
- **ClientFrontend**: Contains the Vue.js frontend

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 14+ and npm
- Ollama installed and running locally

### Backend Setup

```bash
cd LangchainBackend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cd app
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd ClientFrontend
npm install
npm run serve
```

The application will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:8080

## Documentation

For more detailed information, please refer to the following documentation:

- [Tutorial](TUTORIAL.md): Step-by-step guide to setting up and using the application
- [Documentation](DOCUMENTATION.md): Comprehensive documentation of the project architecture and components
- [Changelog](CHANGELOG.md): History of changes and updates to the project

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [LangChain](https://www.langchain.com/) for the LLM framework
- [Ollama](https://ollama.ai/) for the local LLM capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Vue.js](https://vuejs.org/) for the frontend framework
- [Pinia](https://pinia.vuejs.org/) for state management 