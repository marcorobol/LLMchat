<script setup>
import { ref } from 'vue'
import ChatInterface from './components/ChatInterface.vue'
import ModelSelector from './components/ModelSelector.vue'
import axios from 'axios'

// State
const uploadedFiles = ref([])
const messages = ref([])
const isProcessing = ref(false)

const modelSettings = ref({
  provider: 'custom_openai',
  model: 'local-model',
  apiKey: '',
  baseUrl: 'http://bears.disi.unitn.it:1234/v1'
})

// File Handlers
const handleFilesSelected = (files) => {
  uploadedFiles.value = files
  // In a real app, we would upload them immediately or queue them
  // For this demo, we simulate upload and then use them in context
  uploadFilesToBackend(files)
}

const uploadFilesToBackend = async (files) => {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  
  try {
    await axios.post('http://localhost:8000/upload/documents', formData)
    console.log("Files uploaded successfully")
  } catch (e) {
    console.error("Upload failed", e)
  }
}

// Chat Handlers
const handleSendMessage = async (text) => {
  // Add user message
  messages.value.push({
    role: 'user',
    content: text
  })

  isProcessing.value = true

  try {
    const formData = new FormData()
    formData.append('question', text)
    // Send all uploaded filenames as context context
    uploadedFiles.value.forEach(f => {
      formData.append('context_files', f.name)
    })
    
    // Model Params
    formData.append('model_provider', modelSettings.value.provider)
    formData.append('model_id', modelSettings.value.model)
    if (modelSettings.value.apiKey) {
      formData.append('api_key', modelSettings.value.apiKey)
    }
    if (modelSettings.value.baseUrl) {
      formData.append('base_url', modelSettings.value.baseUrl)
    }
    if (modelSettings.value.contextLimit) {
      formData.append('context_limit', modelSettings.value.contextLimit)
    }

    const response = await axios.post('http://localhost:8000/ask', formData)
    
    const data = response.data
    messages.value.push({
      role: 'assistant',
      content: data.answer,
      citations: data.citations || []
    })

  } catch (error) {
    console.error(error)
    messages.value.push({
      role: 'assistant',
      content: "Sorry, I encountered an error connecting to the backend. Is it running?"
    })
  } finally {
    isProcessing.value = false
  }
}
</script>

<template>
  <div class="app-container">
    <a href="https://github.com/marcorobol/LLMchat" target="_blank" class="github-link">
      <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
      </svg>
    </a>
    <main class="main-content">
      <div class="content-wrapper">
        <ModelSelector v-model="modelSettings" />
        <ChatInterface
          :messages="messages"
          :is-loading="isProcessing"
          :uploaded-files="uploadedFiles"
          @send-message="handleSendMessage"
          @files-selected="handleFilesSelected"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
.github-link {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  color: #24292f;
  transition: color 0.2s, transform 0.2s;
}

.github-link:hover {
  color: #000;
  transform: scale(1.1);
}

.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  padding: 20px;
  gap: 20px;
  box-sizing: border-box;
}

.main-content {
  flex: 1;
  display: flex;
  min-width: 0;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

/* Ensure ChatInterface takes remaining height inside content-wrapper */
.content-wrapper :deep(.chat-interface) {
  flex: 1;
}

@media (max-width: 900px) {
  .app-container {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
  }

  .main-content {
    height: 800px;
  }
}
</style>
