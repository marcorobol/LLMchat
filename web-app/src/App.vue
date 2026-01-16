<script setup>
import { ref } from 'vue'
import LawList from './components/LawList.vue'
import FileUpload from './components/FileUpload.vue'
import ChatInterface from './components/ChatInterface.vue'
import ModelSelector from './components/ModelSelector.vue'
import axios from 'axios'

// State
const laws = ref([
  { id: 1, name: 'GDPR Regulation 2016/679', active: true },
  { id: 2, name: 'AI Act Proposal (EU)', active: true }
])

const uploadedFiles = ref([])
const messages = ref([])
const isProcessing = ref(false)

const modelSettings = ref({
  provider: 'custom_openai',
  model: 'local-model',
  apiKey: '',
  baseUrl: 'http://bears.disi.unitn.it:1234/v1'
})

// Law Handlers
const addLaw = (law) => {
  laws.value.push(law)
}

const removeLaw = (id) => {
  laws.value = laws.value.filter(l => l.id !== id)
}

const toggleLaw = (id) => {
  const law = laws.value.find(l => l.id === id)
  if (law) law.active = !law.active
}

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
    <aside class="sidebar-left">
      <LawList 
        :laws="laws" 
        @add-law="addLaw" 
        @remove-law="removeLaw"
        @toggle-law="toggleLaw"
      />
    </aside>

    <main class="main-content">
      <div class="top-section">
        <FileUpload 
          title="Context Documents"
          accept=".pdf,.docx,.txt,.jpg,.png"
          @files-selected="handleFilesSelected"
        />
      </div>

      <div class="bottom-section">
        <div class="content-wrapper">
          <ModelSelector v-model="modelSettings" />
          <ChatInterface 
            :messages="messages" 
            :is-loading="isProcessing"
            @send-message="handleSendMessage"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  padding: 20px;
  gap: 20px;
  box-sizing: border-box;
}

.sidebar-left {
  width: 300px;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0; 
}

.top-section {
  flex: 0 0 15%; 
  min-height: 120px;
}

.bottom-section {
  flex: 1; 
  min-height: 0; 
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
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
  
  .sidebar-left {
    width: 100%;
    height: 300px;
  }

  .main-content {
    height: 800px;
  }
}
</style>
