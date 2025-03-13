# Changelog

All notable changes to the LangChain Ollama Chatbot project will be documented in this file.

## [0.2.0] - 2025-03-14

### Added
- ESLint configuration for the frontend:
  - Added `.eslintrc.js` with Vue 3 specific rules
  - Added `.eslintignore` to exclude certain files from linting
  - Added `vue.config.js` for Vue CLI integration
- Comprehensive documentation about chatbot capabilities
- Project maintenance guidelines in documentation
- Development workflow documentation

### Changed
- Migrated from Vuex to Pinia for state management:
  - Created a new Pinia store for chat functionality
  - Updated components to use the Pinia store
  - Removed Vuex dependencies
- Updated documentation to reflect all changes
- Improved troubleshooting section with ESLint-specific guidance

## [0.1.0] - 2025-03-13

### Added
- Initial project setup with two main components:
  - LangchainBackend: Python FastAPI backend with LangChain and Ollama integration
  - ClientFrontend: Vue.js frontend for the chatbot interface
- Backend features:
  - FastAPI REST API with CORS support
  - LangChain integration with Ollama
  - Conversation memory management
  - API endpoints for chat, history retrieval, and history clearing
- Frontend features:
  - Modern Vue.js 3 application with Vue Router
  - Real-time chat interface with message history
  - Responsive design with clean UI
  - Error handling and loading states
- Documentation:
  - README files for both backend and frontend
  - Environment configuration files
  - API documentation 