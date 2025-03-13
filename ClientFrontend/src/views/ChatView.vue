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
      <form @submit.prevent="handleSendMessage">
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
  --primary-color: #4caf50;
  --accent-color: #45a049;
  --background-color: #f5f5f5;
  --chat-background: #ffffff;
  --text-color: #333333;
  --text-secondary: #666666;
  --border-color: #e0e0e0;
  --message-user-bg: #4caf50;
  --message-user-text: #ffffff;
  --message-assistant-bg: #e9e9e9;
  --message-assistant-text: #333333;
  --input-bg: #ffffff;
  --input-border: #e0e0e0;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  --error-bg: #f8d7da;
  --error-text: #721c24;
  --error-border: #f5c6cb;
}

/* Dark Mode Variables */
.dark-mode {
  --primary-color: #2e7d32;
  --accent-color: #388e3c;
  --background-color: #121212;
  --chat-background: #1e1e1e;
  --text-color: #e0e0e0;
  --text-secondary: #b0b0b0;
  --border-color: #333333;
  --message-user-bg: #2e7d32;
  --message-user-text: #ffffff;
  --message-assistant-bg: #333333;
  --message-assistant-text: #e0e0e0;
  --input-bg: #2a2a2a;
  --input-border: #444444;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  --error-bg: #442a2d;
  --error-text: #f8d7da;
  --error-border: #723c40;
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
  transition: background-color 0.3s ease;
}

.input-container form {
  display: flex;
  gap: 0.5rem;
}

.input-container input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--input-border);
  border-radius: 4px;
  font-size: 1rem;
  background-color: var(--input-bg);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.input-container input::placeholder {
  color: var(--text-secondary);
}

.input-container button {
  padding: 0.75rem 1.5rem;
  background-color: var(--accent-color);
  color: var(--message-user-text);
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  white-space: nowrap;
}

.input-container button:hover:not(:disabled) {
  background-color: var(--primary-color);
  filter: brightness(1.1);
}

.input-container button:disabled {
  background-color: var(--border-color);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.error-message {
  padding: 0.75rem;
  background-color: var(--error-bg);
  color: var(--error-text);
  text-align: center;
  border-top: 1px solid var(--error-border);
  transition: all 0.3s ease;
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