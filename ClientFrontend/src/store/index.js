import axios from 'axios'
import { createStore } from 'vuex'

const API_URL = 'http://localhost:8000'

export default createStore({
  state: {
    messages: [],
    isLoading: false,
    error: null
  },
  getters: {
    getMessages: state => state.messages,
    isLoading: state => state.isLoading,
    hasError: state => state.error !== null,
    getError: state => state.error
  },
  mutations: {
    setLoading(state, isLoading) {
      state.isLoading = isLoading
    },
    setError(state, error) {
      state.error = error
    },
    addMessage(state, message) {
      state.messages.push(message)
    },
    setMessages(state, messages) {
      state.messages = messages
    },
    clearMessages(state) {
      state.messages = []
    }
  },
  actions: {
    async sendMessage({ commit }, message) {
      try {
        commit('setLoading', true)
        commit('setError', null)
        
        // Add user message to the chat
        commit('addMessage', {
          role: 'user',
          content: message
        })
        
        // Send message to the API
        const response = await axios.post(`${API_URL}/chat`, {
          message: message
        })
        
        // Add bot response to the chat
        commit('addMessage', {
          role: 'assistant',
          content: response.data.response
        })
        
        return response.data
      } catch (error) {
        commit('setError', error.message || 'Failed to send message')
        console.error('Error sending message:', error)
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    async fetchHistory({ commit }) {
      try {
        commit('setLoading', true)
        commit('setError', null)
        
        const response = await axios.get(`${API_URL}/history`)
        commit('setMessages', response.data.history)
        
        return response.data
      } catch (error) {
        commit('setError', error.message || 'Failed to fetch history')
        console.error('Error fetching history:', error)
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    
    async clearHistory({ commit }) {
      try {
        commit('setLoading', true)
        commit('setError', null)
        
        await axios.delete(`${API_URL}/history`)
        commit('clearMessages')
        
      } catch (error) {
        commit('setError', error.message || 'Failed to clear history')
        console.error('Error clearing history:', error)
        throw error
      } finally {
        commit('setLoading', false)
      }
    }
  }
}) 