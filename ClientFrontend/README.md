# LangChain Ollama Chatbot Frontend

This is a Vue.js frontend for the LangChain Ollama Chatbot.

## Prerequisites

- Node.js 14+ and npm
- Backend API running (see the LangchainBackend folder)

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

## Features

- Real-time chat with an AI assistant powered by LangChain and Ollama
- Conversation history
- Clear conversation option
- Responsive design

## Project Structure

- `src/components/`: Vue components
- `src/views/`: Vue views/pages
- `src/stores/`: Pinia stores for state management
- `src/assets/`: Static assets
- `src/router.js`: Vue Router configuration
- `src/main.js`: Application entry point 