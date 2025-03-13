<template>
  <div class="chat-container" :class="{ 'dark-mode': isDarkMode }">
    <div class="chat-header">
      <h2>Chat with AI</h2>
      <div class="header-controls">
        <button class="theme-toggle" aria-label="Toggle theme" @click="toggleTheme">
          <span v-if="isDarkMode">🌞</span>
          <span v-else>🌙</span>
        </button>
        <button class="clear-button" @click="clearChat">
          Clear Chat
        </button>
      </div>
    </div>
    
    <div ref="messagesContainer" class="messages-container">
      <div v-if="messages.length === 0" class="empty-state">
        <p>Start a conversation with the AI assistant.</p>
      </div>
      
      <div v-else class="messages">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
        >
          <div class="message-content">
            <p>{{ message.content }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="input-container">
      <form class="chat-form" @submit.prevent="handleSendMessage">
        <div class="chat-icon">
          💬
        </div>
        <input 
          v-model="userInput" 
          type="text" 
          placeholder="Type your message here..." 
          :disabled="chatStore.isLoading"
        >
        <button type="submit" :disabled="chatStore.isLoading || !userInput.trim()">
          <span v-if="chatStore.isLoading">Sending...</span>
          <span v-else>Send</span>
        </button>
      </form>
    </div>
    
    <div v-if="chatStore.hasError" class="error-message">
      <p>{{ chatStore.getError }}</p>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref, watch } from 'vue'
import { useChatStore } from '../stores/chatStore'

export default {
  name: 'ChatView',
  
  setup() {
    const userInput = ref('')
    const messagesContainer = ref(null)
    const chatStore = useChatStore()
    const isDarkMode = ref(false)
    
    const messages = computed(() => chatStore.getMessages)
    
    // Initialize theme based on user preference or system preference
    onMounted(() => {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        isDarkMode.value = savedTheme === 'dark'
      } else {
        // Check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        isDarkMode.value = prefersDark
      }
      
      // Apply theme class to body
      document.body.classList.toggle('dark-mode', isDarkMode.value)
    })
    
    // Watch for theme changes and update localStorage
    watch(isDarkMode, (newValue) => {
      localStorage.setItem('theme', newValue ? 'dark' : 'light')
      document.body.classList.toggle('dark-mode', newValue)
    })
    
    const toggleTheme = () => {
      isDarkMode.value = !isDarkMode.value
    }
    
    const handleSendMessage = async () => {
      if (!userInput.value.trim() || chatStore.isLoading) return
      
      try {
        await chatStore.sendMessage(userInput.value)
        userInput.value = ''
        scrollToBottom()
      } catch (error) {
        console.error('Failed to send message:', error)
      }
    }
    
    const clearChat = async () => {
      try {
        await chatStore.clearHistory()
      } catch (error) {
        console.error('Failed to clear chat:', error)
      }
    }
    
    const scrollToBottom = () => {
      setTimeout(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      }, 100)
    }
    
    onMounted(async () => {
      try {
        await chatStore.fetchHistory()
        scrollToBottom()
      } catch (error) {
        console.error('Failed to fetch chat history:', error)
      }
    })
    
    return {
      userInput,
      messagesContainer,
      chatStore,
      messages,
      handleSendMessage,
      clearChat,
      scrollToBottom,
      isDarkMode,
      toggleTheme
    }
  }
}
</script>

<style scoped>
/* CSS Variables for Light Mode */
:root {
  --primary-color: #2196F3; /* Blue */
  --accent-color: #1976D2; /* Darker Blue */
  --background-color: #FFFFFF; /* Brighter white background */
  --chat-background: #FFFFFF; /* Pure white chat background */
  --text-color: #212121;
  --text-secondary: #757575;
  --border-color: #E0E0E0;
  --message-user-bg: #2196F3;
  --message-user-text: #FFFFFF;
  --message-assistant-bg: #F8F9FA; /* Lighter background for assistant messages */
  --message-assistant-text: #212121;
  --input-bg: #FFFFFF;
  --input-border: #BDBDBD;
  --input-focus-border: #2196F3;
  --input-shadow: rgba(0, 0, 0, 0.08);
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  --error-bg: #FFEBEE;
  --error-text: #C62828;
  --error-border: #FFCDD2;
}

/* Dark Mode Variables */
.dark-mode {
  --primary-color: #1565C0; /* Darker Blue */
  --accent-color: #0D47A1; /* Even Darker Blue */
  --background-color: #000000; /* Pure black background */
  --chat-background: #121212; /* Very dark chat background */
  --text-color: #E0E0E0;
  --text-secondary: #9E9E9E;
  --border-color: #333333;
  --message-user-bg: #1565C0;
  --message-user-text: #FFFFFF;
  --message-assistant-bg: #1A1A1A; /* Darker background for assistant messages */
  --message-assistant-text: #E0E0E0;
  --input-bg: #252525;
  --input-border: #424242;
  --input-focus-border: #1976D2;
  --input-shadow: rgba(0, 0, 0, 0.3);
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  --error-bg: #311B1B;
  --error-text: #EF9A9A;
  --error-border: #4E2C2C;
}

.chat-container {
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  width: 90%;
  margin: 1rem auto;
  height: calc(100vh - 2rem);
  background-color: var(--chat-background);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--primary-color);
  color: var(--message-user-text);
}

.header-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.theme-toggle {
  background-color: transparent;
  border: none;
  color: var(--message-user-text);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  transition: background-color 0.3s;
}

.theme-toggle:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.clear-button {
  background-color: transparent;
  border: 1px solid var(--message-user-text);
  color: var(--message-user-text);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.clear-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background-color: var(--background-color);
  transition: background-color 0.3s ease;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-secondary);
  font-style: italic;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  animation: fadeIn 0.3s ease-in-out;
  transition: background-color 0.3s ease, color 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  align-self: flex-end;
  background-color: var(--message-user-bg);
  color: var(--message-user-text);
  border-bottom-right-radius: 0;
}

.assistant-message {
  align-self: flex-start;
  background-color: var(--message-assistant-bg);
  color: var(--message-assistant-text);
  border-bottom-left-radius: 0;
}

.message-content {
  word-break: break-word;
}

.input-container {
  padding: 1rem;
  background-color: var(--chat-background);
  border-top: 1px solid var(--border-color);
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
  box-shadow: 0 -2px 10px var(--input-shadow);
}

/* Light mode specific container styling */
:root:not(.dark-mode) .chat-container {
  border: 2px solid #E0E0E0;
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.1);
}

/* Light mode specific input container styling */
:root:not(.dark-mode) .input-container {
  background-color: #FFFFFF;
  border-top: 2px solid #E0E0E0;
  box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.05);
}

/* Light mode specific button styling */
:root:not(.dark-mode) .input-container button {
  background-color: #2196F3;
  color: white;
  border: none;
  box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
}

:root:not(.dark-mode) .input-container button:hover:not(:disabled) {
  background-color: #1976D2;
  box-shadow: 0 3px 6px rgba(33, 150, 243, 0.4);
}

.input-container form {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background-color: var(--input-bg);
  border-radius: 8px;
  border: 2px solid var(--input-border);
  box-shadow: 0 2px 8px var(--input-shadow);
  transition: all 0.3s ease;
}

.chat-icon {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin-right: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Light mode specific form styling */
:root:not(.dark-mode) .input-container form {
  background-color: #FFFFFF;
  border: 2px solid #BDBDBD;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

:root:not(.dark-mode) .input-container form:focus-within {
  border-color: #2196F3;
  box-shadow: 0 3px 12px rgba(33, 150, 243, 0.15);
}

.input-container input {
  flex: 1;
  padding: 0.75rem 0.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  background-color: #FFFFFF !important;
  color: #212121;
  transition: all 0.3s ease;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  box-shadow: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.input-container input:focus {
  outline: none;
}

/* Light mode specific input styling - overriding to ensure consistency */
:root:not(.dark-mode) .input-container input {
  background-color: #FFFFFF !important;
  border: none;
  color: #212121;
}

/* Dark mode specific input styling - overriding to ensure consistency */
.dark-mode .input-container input {
  background-color: #FFFFFF !important;
  color: #212121;
}

:root:not(.dark-mode) .input-container input:focus {
  border-color: transparent;
  box-shadow: none;
}

.input-container input::placeholder {
  color: #757575;
}

.input-container button {
  padding: 0.75rem 1.5rem;
  background-color: var(--accent-color);
  color: var(--message-user-text);
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-weight: 500;
}

.input-container button:hover:not(:disabled) {
  background-color: var(--primary-color);
  transform: translateY(-1px);
}

.input-container button:active:not(:disabled) {
  transform: translateY(1px);
}

.input-container button:disabled {
  background-color: var(--border-color);
  color: var(--text-secondary);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* Light mode specific disabled button styling */
:root:not(.dark-mode) .input-container button:disabled {
  background-color: #E0E0E0;
  color: #9E9E9E;
  box-shadow: none;
}

.error-message {
  padding: 0.75rem;
  background-color: var(--error-bg);
  color: var(--error-text);
  text-align: center;
  border-top: 1px solid var(--error-border);
  transition: all 0.3s ease;
}

/* Light mode specific message container styling */
:root:not(.dark-mode) .messages-container {
  background-color: #F5F7FA;
  border-bottom: 2px solid #E0E0E0;
}

/* Light mode specific message styling */
:root:not(.dark-mode) .message {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

:root:not(.dark-mode) .user-message {
  border: 1px solid #1976D2;
  box-shadow: 0 2px 4px rgba(33, 150, 243, 0.2);
}

:root:not(.dark-mode) .assistant-message {
  border: 1px solid #E0E0E0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Responsive Design */
/* Laptop Screens */
@media (min-width: 1024px) and (max-width: 1440px) {
  .chat-container {
    width: 85%;
    max-width: 1100px;
    height: calc(100vh - 3rem);
    margin: 1.5rem auto;
  }
  
  .messages-container {
    padding: 1.5rem;
  }
  
  .message {
    max-width: 75%;
    padding: 1rem 1.25rem;
  }
  
  .input-container {
    padding: 1.25rem;
  }
  
  .input-container input {
    padding: 0.85rem 1.25rem;
    font-size: 1.05rem;
  }
  
  .input-container button {
    padding: 0.85rem 1.75rem;
    font-size: 1.05rem;
  }
}

/* Large Laptop/Desktop Screens */
@media (min-width: 1441px) {
  .chat-container {
    width: 80%;
    max-width: 1300px;
    height: calc(100vh - 4rem);
    margin: 2rem auto;
  }
  
  .chat-header {
    padding: 1.25rem 1.5rem;
  }
  
  .chat-header h2 {
    font-size: 1.5rem;
  }
  
  .messages-container {
    padding: 1.75rem;
  }
  
  .message {
    max-width: 70%;
    padding: 1rem 1.5rem;
    font-size: 1.05rem;
  }
  
  .input-container {
    padding: 1.5rem;
  }
  
  .input-container input {
    padding: 1rem 1.5rem;
    font-size: 1.1rem;
  }
  
  .input-container button {
    padding: 1rem 2rem;
    font-size: 1.1rem;
  }
}

@media (max-width: 850px) {
  .chat-container {
    margin: 0;
    height: 100vh;
    border-radius: 0;
    max-width: 100%;
  }
}

@media (max-width: 600px) {
  .chat-header h2 {
    font-size: 1.2rem;
  }
  
  .message {
    max-width: 90%;
  }
  
  .input-container form {
    flex-direction: column;
  }
  
  .input-container button {
    width: 100%;
  }
  
  .clear-button {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .theme-toggle {
    width: 1.8rem;
    height: 1.8rem;
  }
}

@media (max-width: 400px) {
  .chat-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .header-controls {
    width: 100%;
    justify-content: space-between;
  }
}
</style> 