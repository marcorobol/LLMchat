<script setup>
import { ref, watch } from 'vue'
import { Settings, Cpu, Cloud, Key } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ provider: 'local', model: 'llama3', apiKey: '', baseUrl: '' })
  }
})

const emit = defineEmits(['update:modelValue'])

const settings = ref({ ...props.modelValue })
const showConfig = ref(false)

const formatContext = (chars) => {
  const tokens = Math.round(chars / 3) // Approx 3 chars per token
  if (tokens > 1000000) return `${(tokens/1000000).toFixed(1)}M tok`
  if (tokens > 1000) return `${(tokens/1000).toFixed(0)}k tok`
  return `${tokens} tok`
}

// Heuristic to guess context window based on model name
// Returns limit in characters (approx tokens * 4)
const guessContextWindow = (modelId) => {
  if (!modelId) return 12000 // Default ~3k tokens
  
  const lowerId = modelId.toLowerCase()
  if (lowerId.includes('70b') || lowerId.includes('llama-3.3')) {
    return 131072 * 3 // ~128k tokens (conservative char count)
  }
  if (lowerId.includes('8b') || lowerId.includes('gpt-3.5')) {
    return 16000 // ~4k tokens
  }
  if (lowerId.includes('gpt-4')) {
    return 128000 * 3 
  }
  if (lowerId.includes('devstral')) {
    return 201800 * 3 // Massive context
  }
  // Default fallback
  return 12000
}

const providers = [
  { id: 'custom_openai', name: 'Remote Server', icon: Settings },
  { id: 'local', name: 'Local (Ollama)', icon: Cpu },
  { id: 'openai', name: 'OpenAI', icon: Cloud },
  { id: 'zai', name: 'Z.ai', icon: Cloud }
]

const models = {
  local: ['llama3', 'mistral', 'llava'],
  openai: ['gpt-4o', 'gpt-3.5-turbo'],
  zai: ['glm-4.7', 'glm-4-flash'],
  custom_openai: ['local-model'] // Default, will be populated dynamically
}

const customModels = ref([])

const fetchModels = async () => {
  if (!settings.value.baseUrl) return
  
  try {
    // Construct models URL (handle trailing slash)
    const baseUrl = settings.value.baseUrl.replace(/\/$/, '')
    const url = `${baseUrl}/models`
    
    const response = await fetch(url)
    if (!response.ok) throw new Error('Failed to fetch models')
    
    const data = await response.json()
    if (data.data && Array.isArray(data.data)) {
      customModels.value = data.data.map(m => m.id)
      // Update models object for custom_openai
      models.custom_openai = customModels.value
      // Select first model if current one is not in list
      if (!customModels.value.includes(settings.value.model)) {
        settings.value.model = customModels.value[0]
      }
    }
  } catch (e) {
    console.error("Error fetching models:", e)
    // Fallback or keep existing
  }
}

// Replaced heuristic with backend call
const fetchContextLength = async (modelId) => {
  if (!modelId) return
  
  // Use heuristic as fallback or initial value
  const heuristic = guessContextWindow(modelId)
  
  // But define a reactive property or emit to update it
  // For this demo, let's just make a quick call if provider is custom_openai
  if (settings.value.provider === 'custom_openai') {
    try {
      const response = await fetch(`http://localhost:8000/model/info?model_id=${modelId}`)
      if (response.ok) {
        const data = await response.json()
        if (data.context_length) {
          // Convert tokens to chars ratio (approx 4 chars per token usually, but Python len is chars)
          // Actually context length from SDK is likely in tokens.
          // We need chars for our truncation logic.
          const chars = data.context_length * 3.5 // Approximation
          emit('update:modelValue', { ...settings.value, contextLimit: Math.floor(chars) })
          return
        }
      }
    } catch (e) {
      console.warn("Could not fetch real context length, using heuristic", e)
    }
  }
  
  // Create object with heuristic if API failed
  emit('update:modelValue', { ...settings.value, contextLimit: heuristic })
}

watch(() => settings.value.model, (newModel) => {
  fetchContextLength(newModel)
})

// Fetch models when provider is custom_openai or URL changes
watch(() => [settings.value.provider, settings.value.baseUrl], async ([newProvider, newUrl]) => {
  if (newProvider === 'custom_openai' && newUrl) {
    await fetchModels()
  }
})

import { onMounted } from 'vue'
onMounted(() => {
  if (settings.value.provider === 'custom_openai' && settings.value.baseUrl) {
    fetchModels()
  }
})
</script>

<template>
  <div class="model-selector glass">
    <div class="main-controls">
      <div class="control-row">
        <label>Provider</label>
        <div class="provider-options">
          <button 
            v-for="p in providers" 
            :key="p.id"
            :class="{ active: settings.provider === p.id }"
            @click="settings.provider = p.id; settings.model = models[p.id][0]"
            :title="p.name"
          >
            <component :is="p.icon" size="14" />
            <span class="provider-name">{{ p.name }}</span>
          </button>
        </div>
      </div>

      <div class="control-row">
        <label>Model</label>
        <div class="model-select-wrapper">
          <select v-model="settings.model">
            <option v-for="m in models[settings.provider]" :key="m" :value="m">
              {{ m }} ({{ formatContext(guessContextWindow(m)) }})
            </option>
          </select>
          <button 
            v-if="settings.provider === 'custom_openai'" 
            class="refresh-btn" 
            @click="fetchModels"
            title="Refresh Models"
          >
            ↻
          </button>
          <button class="config-toggle" @click="showConfig = !showConfig" :class="{ active: showConfig }">
            <Settings size="14" />
          </button>
        </div>
      </div>
    </div>

    <!-- Advanced Configuration Panel -->
    <div v-if="showConfig" class="config-panel">
      <div class="form-group" v-if="settings.provider !== 'local'">
        <label>API Key</label>
        <div class="input-wrapper">
          <Key size="14" class="input-icon" />
          <input type="password" v-model="settings.apiKey" placeholder="Enter API Key" />
        </div>
      </div>

      <div class="form-group" v-if="settings.provider === 'custom_openai'">
        <label>Base URL</label>
        <div class="input-wrapper">
          <Settings size="14" class="input-icon" />
          <input type="text" v-model="settings.baseUrl" placeholder="e.g. http://bears.disi.unitn.it:1234/v1" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.model-selector {
  border-radius: var(--radius-sm);
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid var(--glass-border);
  padding: 10px;
}

.main-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-row label {
  width: 60px;
  font-size: 0.8em;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.provider-options {
  display: flex;
  gap: 4px;
  flex: 1;
}

.provider-options button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px;
  font-size: 0.8em;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-muted);
}

.provider-options button.active {
  background: var(--color-primary);
  color: #000;
  border-color: var(--color-primary);
}

/* Hide text on very small screens if needed, but keeping for now */
.provider-name {
  white-space: nowrap;
}

.model-select-wrapper {
  display: flex;
  gap: 5px;
  flex: 1;
}

select {
  flex: 1;
  padding: 6px;
  font-size: 0.9em;
  background: var(--color-bg-surface);
  border: 1px solid var(--glass-border);
  color: var(--color-text-main);
  border-radius: var(--radius-sm);
}

.refresh-btn, .config-toggle {
  padding: 0 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--glass-border);
  color: var(--color-text-main);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.config-toggle.active {
  background: rgba(255, 255, 255, 0.3);
}

.config-panel {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  gap: 8px;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-group label {
  width: 60px;
  font-size: 0.8em;
  color: var(--color-text-muted);
}

.input-wrapper {
  flex: 1;
  position: relative;
}

.input-icon {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
}

input {
  width: 100%;
  padding: 6px 6px 6px 26px;
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  color: white;
  font-size: 0.9em;
}

</style>
