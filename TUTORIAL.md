# LangChain Ollama Chatbot Tutorial

This tutorial will guide you through setting up and using the LangChain Ollama Chatbot application.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.9 or higher
- Node.js 14 or higher and npm
- Ollama (https://ollama.ai/)

## Step 1: Clone the Repository

First, clone the repository to your local machine:

```bash
git clone <repository-url>
cd langchain-ollama-chatbot
```

## Step 2: Set Up the Backend

### Install Ollama

If you haven't already installed Ollama, follow the instructions at https://ollama.ai/ to install it for your operating system.

### Pull the Llama3 Model

Once Ollama is installed, pull the Llama3 model:

```bash
ollama pull llama3
```

### Set Up the Python Environment

Navigate to the LangchainBackend directory and set up a virtual environment:

```bash
cd LangchainBackend
python -m venv venv
```

Activate the virtual environment:

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configure the Backend

The backend is configured using environment variables in the `.env` file. The default configuration should work if Ollama is running locally:

```
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3
```

### Start the Backend Server

Start the FastAPI server:

```bash
cd app
uvicorn main:app --reload
```

The backend API will be available at http://localhost:8000. You can test it by opening this URL in your browser, which should display a welcome message.

## Step 3: Set Up the Frontend

Open a new terminal window and navigate to the ClientFrontend directory:

```bash
cd ClientFrontend
```

Install the required dependencies:

```bash
npm install
```

### Configure the Frontend

The frontend is configured using environment variables in the `.env` file. The default configuration should work if the backend is running locally:

```
VUE_APP_API_URL=http://localhost:8000
```

### Start the Frontend Development Server

Start the Vue.js development server:

```bash
npm run serve
```

The frontend application will be available at http://localhost:8080. Open this URL in your browser to access the chatbot interface.

## Step 4: Using the Chatbot

### Sending Messages

1. Type your message in the input field at the bottom of the chat interface
2. Press Enter or click the Send button to send the message
3. The AI will process your message and respond

### Viewing Conversation History

The conversation history is displayed in the chat interface. User messages appear on the right side, and AI responses appear on the left side.

### Clearing Conversation History

To clear the conversation history, click the "Clear Chat" button in the top-right corner of the chat interface.

## Step 5: Customizing the Application

### Changing the Language Model

To use a different language model, update the `MODEL_NAME` variable in the `.env` file in the LangchainBackend directory. Make sure the model is available in Ollama.

### Customizing the Frontend

The frontend uses CSS variables for styling, which can be found in the `App.vue` file. You can modify these variables to change the appearance of the application.

### Adding Authentication

For production use, you may want to add authentication to the application. This would involve:

1. Adding authentication endpoints to the backend
2. Implementing a login page in the frontend
3. Adding authentication middleware to protect the API endpoints
4. Storing user-specific conversation history

## Troubleshooting

### Backend Issues

- Make sure Ollama is running and accessible at http://localhost:11434
- Check that the Llama3 model is properly installed in Ollama
- Verify that all required Python packages are installed
- Check the console for error messages

### Frontend Issues

- Make sure the backend API is running and accessible
- Check that the `VUE_APP_API_URL` is correctly set in the `.env` file
- Verify that all required npm packages are installed
- Check the browser console for error messages

## Deployment

### Backend Deployment

To deploy the backend to a production environment:

1. Set up a Python environment on your server
2. Install the required dependencies
3. Configure the environment variables
4. Use a production ASGI server like Gunicorn with Uvicorn workers
5. Set up a reverse proxy with Nginx or Apache

### Frontend Deployment

To deploy the frontend to a production environment:

1. Build the production version of the application:
   ```bash
   npm run build
   ```
2. Deploy the contents of the `dist` directory to a web server
3. Configure the web server to serve the application and handle routing

## Conclusion

You now have a fully functional chatbot application using LangChain with Ollama for the backend and Vue.js for the frontend. You can customize and extend the application to suit your needs. 