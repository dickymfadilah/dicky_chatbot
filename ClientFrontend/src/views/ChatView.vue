<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>Chat with AI</h2>
      <button @click="clearChat" class="clear-button">Clear Chat</button>
    </div>
    
    <div class="messages-container" ref="messagesContainer">
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
          :disabled="isLoading"
        />
        <button type="submit" :disabled="isLoading || !userInput.trim()">
          <span v-if="isLoading">Sending...</span>
          <span v-else>Send</span>
        </button>
      </form>
    </div>
    
    <div v-if="hasError" class="error-message">
      <p>{{ getError }}</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'ChatView',
  
  setup() {
    const userInput = ref('')
    const messagesContainer = ref(null)
    
    return {
      userInput,
      messagesContainer
    }
  },
  
  computed: {
    ...mapGetters([
      'getMessages',
      'isLoading',
      'hasError',
      'getError'
    ]),
    
    messages() {
      return this.getMessages
    }
  },
  
  methods: {
    ...mapActions([
      'sendMessage',
      'fetchHistory',
      'clearHistory'
    ]),
    
    async handleSendMessage() {
      if (!this.userInput.trim() || this.isLoading) return
      
      try {
        await this.sendMessage(this.userInput)
        this.userInput = ''
        this.scrollToBottom()
      } catch (error) {
        console.error('Failed to send message:', error)
      }
    },
    
    async clearChat() {
      try {
        await this.clearHistory()
      } catch (error) {
        console.error('Failed to clear chat:', error)
      }
    },
    
    scrollToBottom() {
      setTimeout(() => {
        if (this.messagesContainer) {
          this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight
        }
      }, 100)
    }
  },
  
  watch: {
    messages() {
      this.scrollToBottom()
    }
  },
  
  async mounted() {
    try {
      await this.fetchHistory()
      this.scrollToBottom()
    } catch (error) {
      console.error('Failed to fetch history:', error)
    }
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 2rem auto;
  height: calc(100vh - 150px);
  background-color: var(--white);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--primary-color);
  color: var(--white);
}

.clear-button {
  background-color: transparent;
  border: 1px solid var(--white);
  color: var(--white);
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
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
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
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  align-self: flex-end;
  background-color: var(--primary-color);
  color: var(--white);
  border-bottom-right-radius: 0;
}

.assistant-message {
  align-self: flex-start;
  background-color: var(--light-gray);
  color: var(--text-color);
  border-bottom-left-radius: 0;
}

.message-content {
  word-break: break-word;
}

.input-container {
  padding: 1rem;
  background-color: var(--white);
  border-top: 1px solid var(--light-gray);
}

.input-container form {
  display: flex;
  gap: 0.5rem;
}

.input-container input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--light-gray);
  border-radius: 4px;
  font-size: 1rem;
}

.input-container button {
  padding: 0.75rem 1.5rem;
  background-color: var(--accent-color);
  color: var(--white);
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.input-container button:hover:not(:disabled) {
  background-color: #3da978;
}

.input-container button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  padding: 0.75rem;
  background-color: #f8d7da;
  color: #721c24;
  text-align: center;
  border-top: 1px solid #f5c6cb;
}
</style> 