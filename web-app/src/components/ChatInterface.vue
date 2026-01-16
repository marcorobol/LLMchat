<script setup>
import { ref, nextTick, watch } from 'vue'
import { Send, Bot, User, Cpu } from 'lucide-vue-next'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send-message'])
const newMessage = ref('')
const messagesContainer = ref(null)

const sendMessage = () => {
  if (!newMessage.value.trim() || props.isLoading) return
  emit('send-message', newMessage.value)
  newMessage.value = ''
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(() => props.messages, scrollToBottom, { deep: true })
</script>

<template>
  <div class="chat-interface glass">
    <div class="chat-header">
      <Bot class="header-icon" />
      <div class="header-info">
        <h3>Assistant</h3>
        <span class="status">AI Powered Analysis</span>
      </div>
    </div>

    <div class="messages-area" ref="messagesContainer">
      <div v-if="messages.length === 0" class="welcome-message">
        <Cpu class="welcome-icon" :size="48" />
        <h3>How can I help you today?</h3>
        <p>Upload documents and laws to get started.</p>
      </div>

      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message-wrapper"
        :class="msg.role"
      >
        <div class="avatar">
          <User v-if="msg.role === 'user'" size="20" />
          <Bot v-else size="20" />
        </div>
        
        <div class="message-content">
          <div class="text">{{ msg.content }}</div>
          
          <div v-if="msg.citations && msg.citations.length > 0" class="citations">
            <span class="citation-label">Sources:</span>
            <div class="citation-tags">
              <span v-for="(cit, idx) in msg.citations" :key="idx" class="tag">
                {{ cit }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="message-wrapper assistant loading">
        <div class="avatar"><Bot size="20" /></div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="input-area">
      <div class="input-wrapper">
        <textarea 
          v-model="newMessage" 
          placeholder="Ask a question about your documents..." 
          @keydown.enter.prevent="sendMessage"
        ></textarea>
        <button 
          @click="sendMessage" 
          class="send-btn primary-btn"
          :disabled="!newMessage.trim() || isLoading"
        >
          <Send size="20" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.chat-header {
  padding: 12px 15px; /* Reduced */
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--glass-border);
}

.header-icon {
  width: 32px; /* Reduced */
  height: 32px; /* Reduced */
  padding: 6px;
  background: var(--color-primary);
  color: #000;
  border-radius: 50%;
}

.header-info h3 {
  margin: 0;
  font-size: 1em; /* Reduced */
}

.status {
  font-size: 0.75em;
  color: var(--color-primary);
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: rgba(0, 0, 0, 0.2);
}

.welcome-message {
  align-self: center;
  text-align: center;
  margin-top: auto;
  margin-bottom: auto;
  color: var(--color-text-muted);
  opacity: 0.7;
}

.welcome-icon {
  margin-bottom: 20px;
  color: var(--color-primary);
}

.message-wrapper {
  display: flex;
  gap: 15px;
  max-width: 85%;
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  min-width: 36px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-card);
  border: 1px solid var(--glass-border);
}

.message-wrapper.user .avatar {
  background: var(--color-secondary);
}

.message-wrapper.assistant .avatar {
  background: var(--color-primary);
  color: #000;
}

.message-content {
  background: var(--color-bg-card);
  padding: 15px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  line-height: 1.6;
}

.message-wrapper.user .message-content {
  background: rgba(112, 0, 255, 0.1);
  border-color: rgba(112, 0, 255, 0.3);
}

.citations {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.citation-label {
  font-size: 0.8em;
  color: var(--color-text-muted);
  margin-right: 5px;
}

.tag {
  font-size: 0.75em;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: var(--color-primary);
}

.input-area {
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid var(--glass-border);
}

.input-wrapper {
  display: flex;
  gap: 8px;
  background: var(--color-bg-surface);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  resize: none;
  height: 40px; /* Reduced */
  padding: 10px;
  font-size: 0.95em;
}

textarea:focus {
  outline: none;
  border-color: transparent;
}

.send-btn {
  width: 50px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.typing-indicator span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: var(--color-text-muted);
  border-radius: 50%;
  animation: typing 1s infinite;
  margin: 0 2px;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 100% { transform: translateY(0); opacity: 0.6; }
  50% { transform: translateY(-5px); opacity: 1; }
}
</style>
