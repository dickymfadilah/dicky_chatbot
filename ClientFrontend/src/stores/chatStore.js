import axios from 'axios'
import { defineStore } from 'pinia'

const API_URL = 'http://localhost:8000'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    isLoading: false,
    error: null,
    collections: []
  }),
  
  getters: {
    getMessages: (state) => state.messages,
    hasError: (state) => state.error !== null,
    getError: (state) => state.error,
    getCollections: (state) => state.collections
  },
  
  actions: {
    async sendMessage(message) {
      try {
        this.isLoading = true
        this.error = null
        
        // Add user message to the chat
        this.messages.push({
          role: 'user',
          content: message
        })
        
        // Send message to the API
        const response = await axios.post(`${API_URL}/chat`, {
          message: message
        })
        
        // Add bot response to the chat
        this.messages.push({
          role: 'assistant',
          content: response.data.response
        })
        
        return response.data
      } catch (error) {
        this.error = error.message || 'Failed to send message'
        console.error('Error sending message:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchHistory() {
      try {
        this.isLoading = true
        this.error = null
        
        const response = await axios.get(`${API_URL}/history`)
        this.messages = response.data.history
        
        return response.data
      } catch (error) {
        this.error = error.message || 'Failed to fetch history'
        console.error('Error fetching history:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async clearHistory() {
      try {
        this.isLoading = true
        this.error = null
        
        await axios.delete(`${API_URL}/history`)
        this.messages = []
        
      } catch (error) {
        this.error = error.message || 'Failed to clear history'
        console.error('Error clearing history:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchCollections() {
      try {
        this.isLoading = true
        this.error = null
        
        const response = await axios.get(`${API_URL}/collections`)
        this.collections = response.data.collections
        
        return response.data.collections
      } catch (error) {
        this.error = error.message || 'Failed to fetch collections'
        console.error('Error fetching collections:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchCollectionData(collectionName, limit = 10, skip = 0) {
      try {
        this.isLoading = true
        this.error = null
        
        const response = await axios.get(`${API_URL}/collection/${collectionName}`, {
          params: { limit, skip }
        })
        
        return response.data.data
      } catch (error) {
        this.error = error.message || 'Failed to fetch collection data'
        console.error('Error fetching collection data:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
}) 