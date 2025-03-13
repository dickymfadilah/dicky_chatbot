# LangChain Ollama Chatbot

A modern chatbot application built with LangChain, Ollama, FastAPI, and Vue.js.

![LangChain Ollama Chatbot](https://via.placeholder.com/800x400?text=LangChain+Ollama+Chatbot)

## Overview

This project implements a full-stack chatbot application with the following components:

- **Backend**: Python FastAPI application with LangChain and Ollama integration
- **Frontend**: Vue.js application with a modern, responsive UI

The chatbot allows users to have natural language conversations with an AI assistant powered by Ollama's language models.

## Features

- Real-time chat interface
- Conversation history management
- Clean, modern UI with responsive design
- Easy configuration and deployment
- Cross-platform compatibility

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