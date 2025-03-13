# Langchain Ollama Chatbot Documentation

## Overview

This project implements a chatbot using Langchain with Ollama for the backend and Vue.js with Pinia for the frontend. The chatbot leverages the Llama 3 model to provide conversational AI capabilities.

## Architecture

The application consists of two main components:

1. **LangchainBackend**: A Python FastAPI application that integrates Langchain with Ollama.
2. **ClientFrontend**: A Vue.js application that provides a user interface for interacting with the chatbot.

## Chatbot Capabilities

### Current Features

1. **General Conversation**
   - Natural language interactions
   - Contextual responses
   - Conversational flow

2. **Stateful Conversations**
   - Conversation memory using `ConversationBufferMemory`
   - Context retention within a session
   - Reference to previous messages in the current conversation

3. **Knowledge Base**
   - General knowledge from Llama 3's training data
   - Basic facts and information
   - Conceptual explanations
   - Language understanding and generation

### What You Can Ask

The chatbot can respond to a variety of queries, including:

1. **General Knowledge Questions**
   - "What is photosynthesis?"
   - "Who wrote Pride and Prejudice?"
   - "Explain the theory of relativity"

2. **Conceptual Explanations**
   - "Explain quantum computing in simple terms"
   - "How does blockchain work?"
   - "What is machine learning?"

3. **Language Tasks**
   - "Help me write an email to my boss"
   - "Suggest synonyms for 'happy'"
   - "Proofread this paragraph"

4. **Simple Reasoning**
   - "If I have 5 apples and give away 2, how many do I have left?"
   - "What's the next number in this sequence: 2, 4, 8, 16...?"

5. **Creative Content**
   - "Write a short poem about nature"
   - "Create a brief story about a space adventure"
   - "Generate ideas for a birthday celebration"

### Information Limitations

1. **Training Cutoff**
   - The Llama 3 model has a knowledge cutoff date
   - No awareness of events or information after that date

2. **No Internet Access**
   - Cannot look up real-time information
   - No access to current news, weather, or other dynamic data

3. **No Document Knowledge**
   - No access to specific documents or databases unless explicitly added
   - Limited to knowledge in its training data

4. **No Specialized Tools**
   - No built-in calculators, code execution, or data analysis tools
   - Cannot perform complex mathematical operations or run code

## Technical Implementation

### Backend (Langchain + Ollama)

The backend uses:
- FastAPI for the web server
- Langchain for the conversation chain and memory
- Ollama with the Llama 3 model for text generation

Key components:
- `ConversationChain`: Manages the conversation flow
- `ConversationBufferMemory`: Stores conversation history
- Ollama LLM: Generates responses based on the input and conversation history

### Frontend (Vue.js + Pinia)

The frontend uses:
- Vue.js 3 for the UI framework
- Pinia for state management
- Axios for API communication

Key components:
- Chat interface with message history
- Input form for user messages
- State management for conversation history and loading states

#### Code Quality Tools

The frontend includes the following code quality tools:

- **ESLint**: For code linting and enforcing consistent code style
  - Configuration in `.eslintrc.js`
  - Ignore patterns in `.eslintignore`
  - Integrated with Vue CLI via `vue.config.js`
  - Rules customized for Vue 3 development

## API Endpoints

The backend provides the following API endpoints:

1. `GET /`: Welcome message
2. `POST /chat`: Send a message to the chatbot
3. `GET /history`: Retrieve conversation history
4. `DELETE /history`: Clear conversation history

## Potential Enhancements

Future improvements could include:

1. **Document Retrieval**
   - Integrate Langchain's document loaders and retrievers
   - Allow the chatbot to access specific knowledge bases
   - Implement RAG (Retrieval-Augmented Generation) for more accurate responses

2. **Tool Integration**
   - Add specialized tools for tasks like web searches
   - Implement calculators or other utility functions
   - Connect to external APIs for real-time data

3. **Model Improvements**
   - Switch to different Ollama models for specific use cases
   - Fine-tune the model on domain-specific data
   - Implement model fallbacks for different types of queries

4. **Structured Output**
   - Add output parsers for structured data
   - Implement JSON or XML formatting for machine-readable responses
   - Create specialized response templates for different query types

5. **Advanced Memory**
   - Implement more sophisticated memory mechanisms
   - Add long-term storage for user preferences
   - Create user profiles for personalized interactions

## Usage Guide

### Starting the Application

1. **Backend**
   ```bash
   cd LangchainBackend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**
   ```bash
   cd ClientFrontend
   npm install
   npm run serve
   ```

3. Access the application at `http://localhost:8080`

### Using the Chatbot

1. Type your message in the input field at the bottom of the chat interface
2. Press Enter or click the Send button to send your message
3. The chatbot will process your message and respond
4. You can clear the conversation history using the "Clear Chat" button

### Development Workflow

1. **Code Style and Linting**
   ```bash
   cd ClientFrontend
   npm run lint -- --fix
   ```
   This will automatically fix any linting issues in the frontend code.

## Troubleshooting

Common issues and solutions:

1. **Backend Connection Errors**
   - Ensure Ollama is running and the Llama 3 model is installed
   - Check that the backend server is running on the expected port
   - Verify CORS settings if accessing from a different domain

2. **Slow Responses**
   - Ollama performance depends on your hardware
   - Consider using a smaller model if responses are too slow
   - Check system resources and close other intensive applications

3. **Memory Issues**
   - Long conversations may consume more memory
   - Use the clear history function periodically
   - Consider implementing a message limit if needed

4. **ESLint Issues**
   - If you encounter ESLint errors, run `npm run lint -- --fix` in the ClientFrontend directory
   - Check the ESLint configuration in `.eslintrc.js` if you need to customize rules
   - Add files to `.eslintignore` if they should be excluded from linting

## Project Maintenance Guidelines

1. **Documentation Updates**
   - Update documentation whenever you make changes to the codebase
   - Document new features, configuration changes, and bug fixes
   - Keep API documentation up-to-date with any endpoint changes
   - Include examples for new functionality

2. **Version Control**
   - Use descriptive commit messages
   - Create branches for new features or bug fixes
   - Merge changes only after testing

3. **Testing**
   - Test backend API endpoints after making changes
   - Verify frontend functionality in different browsers
   - Check mobile responsiveness for UI changes 