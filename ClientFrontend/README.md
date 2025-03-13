# LangChain Ollama Chatbot Frontend

This is a Vue.js frontend for the LangChain Ollama Chatbot.

## Overview

This frontend application provides a user-friendly interface for interacting with the LangChain Ollama chatbot. It's built with Vue.js 3 and uses Pinia for state management.

## Prerequisites

- Node.js 14+ and npm
- Backend API running (see the LangchainBackend folder)

## Features

- Modern, responsive chat interface
- Real-time interaction with the AI assistant
- Conversation history management
- Clear and intuitive user experience
- Pinia state management for efficient data handling

## Chatbot Capabilities

Through the interface, you can interact with the Llama 3 model to:

### Ask Questions About:
- General knowledge and facts
- Conceptual explanations
- Historical events and figures
- Scientific principles
- Language and definitions

### Request Help With:
- Writing and composition
- Language suggestions
- Creative content generation
- Simple problem-solving
- Idea generation

### Limitations:
- The chatbot cannot access the internet or real-time information
- It only knows information from its training data
- It cannot perform complex calculations or execute code
- It has no access to personal data unless provided in the conversation

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Create a `.env` file (optional):
   ```
   VUE_APP_API_URL=http://localhost:8000
   ```

## Running the Application

1. Start the development server:
   ```
   npm run serve
   ```

2. The application will be available at http://localhost:8080

## Building for Production

1. Build the application:
   ```
   npm run build
   ```

2. The built files will be in the `dist` directory, which can be deployed to a web server.

## Project Structure

- `src/components/`: Vue components
- `src/views/`: Vue views/pages
- `src/stores/`: Pinia stores for state management
- `src/assets/`: Static assets
- `src/router.js`: Vue Router configuration
- `src/main.js`: Application entry point

## State Management with Pinia

This application uses Pinia for state management, which provides:

- Intuitive and type-safe store definitions
- Excellent developer experience with auto-completion
- Modular store design for better code organization
- Efficient reactivity system
- DevTools integration for debugging

The main store is `chatStore.js`, which handles:
- Message history management
- API communication with the backend
- Loading states and error handling 