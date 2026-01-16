<script setup>
import { ref } from 'vue'
import { UploadCloud, FileText, X } from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    default: 'Upload Documents'
  },
  accept: {
    type: String,
    default: '.pdf,.txt,.docx'
  }
})

const emit = defineEmits(['files-selected'])

const isDragging = ref(false)
const selectedFiles = ref([])

const onDragOver = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const onDragLeave = (e) => {
  e.preventDefault()
  isDragging.value = false
}

const onDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  handleFiles(e.dataTransfer.files)
}

const onFileSelect = (e) => {
  handleFiles(e.target.files)
}

const handleFiles = (files) => {
  const newFiles = Array.from(files)
  // validation logic can go here
  selectedFiles.value = [...selectedFiles.value, ...newFiles]
  emit('files-selected', selectedFiles.value)
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  emit('files-selected', selectedFiles.value)
}
</script>

<template>
  <div class="file-upload-container glass">
    <h3 class="title">{{ title }}</h3>
    
    <div 
      class="drop-zone"
      :class="{ 'dragging': isDragging }"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
      @click="$refs.fileInput.click()"
    >
      <input 
        type="file" 
        ref="fileInput" 
        class="hidden-input" 
        multiple 
        :accept="accept"
        @change="onFileSelect"
      />
      
      <div class="upload-icon-wrapper">
        <UploadCloud :size="48" class="upload-icon" />
      </div>
      <p class="cta-text">Click or drag files to upload</p>
      <p class="sub-text">Supported: {{ accept }}</p>
    </div>

    <div v-if="selectedFiles.length > 0" class="file-list">
      <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
        <div class="file-info">
          <FileText size="16" class="file-icon" />
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</span>
        </div>
        <button @click="removeFile(index)" class="remove-btn">
          <X size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.file-upload-container {
  padding: 20px;
  border-radius: var(--radius-md);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.title {
  margin: 0 0 15px 0;
  font-weight: 600;
  color: var(--color-primary);
}

.drop-zone {
  flex: 1;
  border: 2px dashed var(--glass-border);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  cursor: pointer;
  transition: var(--transition-normal);
  background: rgba(255, 255, 255, 0.02);
  min-height: 150px;
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--color-primary);
  background: rgba(0, 240, 255, 0.05);
}

.upload-icon-wrapper {
  margin-bottom: 10px;
  color: var(--color-text-muted);
  transition: var(--transition-normal);
}

.drop-zone:hover .upload-icon-wrapper {
  color: var(--color-primary);
  transform: translateY(-5px);
}

.cta-text {
  margin: 5px 0;
  font-weight: 500;
}

.sub-text {
  font-size: 0.8em;
  color: var(--color-text-muted);
}

.hidden-input {
  display: none;
}

.file-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--glass-border);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
  font-size: 0.9em;
}

.file-size {
  font-size: 0.8em;
  color: var(--color-text-muted);
}

.remove-btn {
  background: transparent;
  padding: 4px;
  color: var(--color-text-muted);
}

.remove-btn:hover {
  color: #ff4d4d;
  background: rgba(255, 77, 77, 0.1);
}
</style>
