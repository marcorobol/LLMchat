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

const formatContext = (tokens) => {
  if (tokens > 1000000) return `${(tokens/1000000).toFixed(1)}M tok`
  if (tokens > 1000) return `${(tokens/1000).toFixed(0)}k tok`
  return `${tokens} tok`
}

// Heuristic to guess context window based on model name
// Returns limit in tokens
const guessContextWindow = (modelId) => {
  if (!modelId) return 4000 // Default ~4k tokens

  const lowerId = modelId.toLowerCase()
  if (lowerId.includes('70b') || lowerId.includes('llama-3.3')) {
    return 131072 // ~128k tokens
  }
  if (lowerId.includes('8b') || lowerId.includes('gpt-3.5')) {
    return 16000 // ~16k tokens
  }
  if (lowerId.includes('gpt-4')) {
    return 128000 // ~128k tokens
  }
  if (lowerId.includes('devstral')) {
    return 393216 // ~393k tokens
  }
  // Default fallback
  return 4000
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
const modelsInfo = ref({}) // Store full model info including state

const getStateColor = (state) => {
  switch (state) {
    case 'loaded': return '#4ade80'
    case 'loading': return '#fbbf24'
    default: return '#9ca3af'
  }
}

const getStateLabel = (state) => {
  switch (state) {
    case 'loaded': return '●'
    case 'loading': return '◐'
    default: return '○'
  }
}

const fetchModels = async () => {
  if (!settings.value.baseUrl) return

  try {
    // Use backend endpoint to get models with state
    const response = await fetch(`http://localhost:8000/models`)
    if (!response.ok) throw new Error('Failed to fetch models')

    const data = await response.json()
    if (data.data && Array.isArray(data.data)) {
      customModels.value = data.data.map(m => m.id)
      // Store full model info
      modelsInfo.value = {}
      data.data.forEach(m => {
        modelsInfo.value[m.id] = m
      })
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

const loadingModel = ref(null)
const unloadingModel = ref(null)

const loadModel = async (modelId) => {
  loadingModel.value = modelId
  try {
    const response = await fetch(`http://localhost:8000/models/${encodeURIComponent(modelId)}/load`, {
      method: 'POST'
    })
    if (response.ok) {
      // Refresh models to get updated state
      await fetchModels()
    } else {
      console.error('Failed to load model')
    }
  } catch (e) {
    console.error('Error loading model:', e)
  } finally {
    loadingModel.value = null
  }
}

const unloadModel = async (modelId) => {
  unloadingModel.value = modelId
  try {
    const response = await fetch(`http://localhost:8000/models/${encodeURIComponent(modelId)}/unload`, {
      method: 'POST'
    })
    if (response.ok) {
      // Refresh models to get updated state
      await fetchModels()
    } else {
      console.error('Failed to unload model')
    }
  } catch (e) {
    console.error('Error unloading model:', e)
  } finally {
    unloadingModel.value = null
  }
}

// Get context limit in characters for the backend
const fetchContextLength = async (modelId) => {
  if (!modelId) return

  // Convert tokens to characters (approx 3.5 chars per token)
  const tokensToChars = (tokens) => Math.floor(tokens * 3.5)

  // First try to use already-loaded model info from API
  if (modelsInfo.value[modelId]?.max_context_length) {
    const tokens = modelsInfo.value[modelId].max_context_length
    emit('update:modelValue', { ...settings.value, contextLimit: tokensToChars(tokens) })
    return
  }

  // Use heuristic as fallback
  const heuristicTokens = guessContextWindow(modelId)
  emit('update:modelValue', { ...settings.value, contextLimit: tokensToChars(heuristicTokens) })
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
        <div class="model-actions">
          <button
            v-if="settings.provider === 'custom_openai'"
            class="refresh-btn"
            @click="fetchModels"
            title="Refresh Models"
          >
            ↻ Refresh
          </button>
          <button class="config-toggle" @click="showConfig = !showConfig" :class="{ active: showConfig }">
            <Settings size="14" />
          </button>
        </div>
      </div>

      <div class="models-grid">
        <div
          v-for="m in models[settings.provider]"
          :key="m"
          class="model-card"
          :class="{ selected: settings.model === m }"
          @click="settings.model = m"
        >
          <div class="model-state" :style="{ color: getStateColor(modelsInfo[m]?.state) }">
            {{ getStateLabel(modelsInfo[m]?.state) }}
          </div>
          <div class="model-name">{{ m }}</div>
          <div class="model-context">
            {{ formatContext(modelsInfo[m]?.max_context_length || guessContextWindow(m)) }}
          </div>
          <div
            v-if="settings.provider === 'custom_openai'"
            class="model-actions-card"
            @click.stop
          >
            <button
              v-if="modelsInfo[m]?.state === 'loaded'"
              @click="unloadModel(m)"
              class="action-btn unload-btn"
              :disabled="unloadingModel === m"
              title="Unload model"
            >
              {{ unloadingModel === m ? '...' : '−' }}
            </button>
            <button
              v-else
              @click="loadModel(m)"
              class="action-btn load-btn"
              :disabled="loadingModel === m || modelsInfo[m]?.state === 'loading'"
              title="Load model"
            >
              {{ loadingModel === m ? '...' : '+' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced Configuration Panel -->
    <div v-if="showConfig" class="config-panel">
      <div class="state-legend" v-if="settings.provider === 'custom_openai' && Object.keys(modelsInfo).length > 0">
        <span class="legend-item"><span class="state-symbol loaded"></span> Loaded</span>
        <span class="legend-item"><span class="state-symbol loading"></span> Loading</span>
        <span class="legend-item"><span class="state-symbol not-loaded"></span> Not Loaded</span>
      </div>

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

.model-actions {
  display: flex;
  gap: 5px;
  margin-left: auto;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
  margin-top: 8px;
}

.model-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 12px;
  cursor: pointer;
  transition: var(--transition-normal);
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: relative;
}

.model-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 240, 255, 0.3);
}

.model-card.selected {
  background: rgba(0, 240, 255, 0.1);
  border-color: var(--color-primary);
}

.model-state {
  font-size: 1.2em;
  align-self: flex-end;
}

.model-name {
  font-weight: 500;
  font-size: 0.9em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.model-context {
  font-size: 0.75em;
  color: var(--color-text-muted);
}

.model-actions-card {
  position: absolute;
  top: 8px;
  left: 8px;
}

.action-btn {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: var(--transition-normal);
  background: rgba(0, 0, 0, 0.3);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.load-btn {
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.3);
}

.load-btn:hover:not(:disabled) {
  background: rgba(74, 222, 128, 0.2);
}

.unload-btn {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.3);
}

.unload-btn:hover:not(:disabled) {
  background: rgba(248, 113, 113, 0.2);
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

.state-legend {
  display: flex;
  gap: 15px;
  padding: 8px 0;
  font-size: 0.75em;
  color: var(--color-text-muted);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.state-symbol {
  font-size: 1.2em;
}

.state-symbol.loaded {
  color: #4ade80;
}

.state-symbol.loading {
  color: #fbbf24;
}

.state-symbol.not-loaded {
  color: #9ca3af;
}

</style>
