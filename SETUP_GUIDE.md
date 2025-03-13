# Setup Guide for LangChain with Ollama

This guide will walk you through setting up your environment for using LangChain with Ollama to create a chatbot application.

## System Requirements

### Hardware Requirements
- **CPU**: Modern multi-core processor (4+ cores recommended)
- **RAM**: Minimum 8GB, 16GB+ recommended for larger models
- **Storage**: At least 10GB of free disk space for model files
- **GPU**: Optional but recommended for faster inference (NVIDIA GPU with CUDA support)

### Software Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.9+ (3.10 or 3.11 recommended)
- **Package Manager**: pip (latest version)
- **Git**: For cloning repositories (if needed)

## Installation Steps

### Step 1: Install Ollama

1. Download Ollama for your operating system from the official website:
   - Windows: https://ollama.com/download/windows
   - macOS: https://ollama.com/download/mac
   - Linux: https://ollama.com/download/linux

2. Run the installer and follow the on-screen instructions.

3. Verify installation by opening a terminal/command prompt and running:
   ```bash
   ollama --version
   ```

### Step 2: Set up Python Environment

1. Ensure you have Python 3.9+ installed:
   ```bash
   python --version
   ```

2. Update pip to the latest version:
   ```bash
   python -m pip install --upgrade pip
   ```

3. (Optional) Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

### Step 3: Install Required Python Packages

1. Navigate to the LangchainBackend directory:
   ```bash
   cd LangchainBackend
   ```

2. Install the required packages:
   ```bash
   pip install --user -r requirements.txt
   ```

### Step 4: Download the Llama 3 Model

1. Pull the Llama 3 model using Ollama:
   ```bash
   ollama pull llama3
   ```

   This will download the model, which may take some time depending on your internet connection.

2. Verify the model is installed:
   ```bash
   ollama list
   ```

### Step 5: Configure the Application

1. Ensure the `.env` file in the LangchainBackend directory contains the correct configuration:
   ```
   OLLAMA_BASE_URL=http://localhost:11434
   MODEL_NAME=llama3
   ```

2. You can modify these settings if needed, for example, if you're running Ollama on a different port or want to use a different model.

## Running the Application

### Backend

1. Start the Ollama service (if not already running):
   ```bash
   # This command may vary depending on your OS
   # On Windows, Ollama typically runs as a service after installation
   ```

2. Navigate to the LangchainBackend directory:
   ```bash
   cd LangchainBackend
   ```

3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

   The server will start on http://localhost:8000 by default.

### Frontend

1. Navigate to the ClientFrontend directory:
   ```bash
   cd ClientFrontend
   ```

2. Install the frontend dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run serve
   ```

   The frontend will be available at http://localhost:8080.

## Troubleshooting

### Common Issues

1. **Ollama Not Found**
   - Ensure Ollama is installed correctly
   - Check if the Ollama service is running
   - Verify the PATH environment variable includes the Ollama executable

2. **Model Download Issues**
   - Check your internet connection
   - Ensure you have enough disk space
   - Try downloading a smaller model first (e.g., `ollama pull tinyllama`)

3. **Python Package Installation Errors**
   - Try using the `--user` flag: `pip install --user -r requirements.txt`
   - Update pip: `python -m pip install --upgrade pip`
   - Check for conflicting dependencies

4. **Backend Connection Errors**
   - Verify Ollama is running with `ollama list`
   - Check the OLLAMA_BASE_URL in your .env file
   - Ensure the correct ports are open and not blocked by a firewall

5. **Slow Model Performance**
   - Consider using a smaller model if you don't have a GPU
   - Close other resource-intensive applications
   - Check system resource usage during model inference

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/README.md)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/guide/introduction.html)

## Next Steps

After setting up your environment, you can:

1. Customize the chatbot's behavior by modifying the LangChain chain in `app/main.py`
2. Add document retrieval capabilities using LangChain's document loaders and retrievers
3. Implement additional API endpoints for specific functionality
4. Enhance the frontend UI for a better user experience 