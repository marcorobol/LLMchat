<script setup>
import { ref } from 'vue'
import { Book, Plus, Trash2, CheckCircle2 } from 'lucide-vue-next'

const props = defineProps({
  laws: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['add-law', 'remove-law', 'toggle-law'])

const newLawName = ref('')

const handleAddLaw = () => {
  // In a real scenario, this might trigger a file upload
  // For now we just simulate adding a "law" entry
  if (!newLawName.value) return
  emit('add-law', { id: Date.now(), name: newLawName.value, active: true })
  newLawName.value = ''
}
</script>

<template>
  <div class="law-list-container glass">
    <div class="header">
      <h3>
        <Book class="icon" size="20" />
        Regulations
      </h3>
      <span class="count">{{ laws.length }} Active</span>
    </div>

    <div class="list-content">
      <div 
        v-for="law in laws" 
        :key="law.id" 
        class="law-item"
        :class="{ 'active': law.active }"
        @click="emit('toggle-law', law.id)"
      >
        <div class="law-info">
          <CheckCircle2 v-if="law.active" size="18" class="status-icon active" />
          <div v-else class="status-circle"></div>
          <span class="law-name">{{ law.name }}</span>
        </div>
        <button @click.stop="emit('remove-law', law.id)" class="delete-btn">
          <Trash2 size="16" />
        </button>
      </div>
      <div v-if="laws.length === 0" class="empty-state">
        No regulations loaded.
      </div>
    </div>

    <div class="add-law-section">
      <input 
        v-model="newLawName" 
        placeholder="Add Regulation (Mock)..." 
        @keyup.enter="handleAddLaw"
      />
      <button @click="handleAddLaw" class="add-btn">
        <Plus size="20" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.law-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.header {
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--glass-border);
}

.header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1em;
  color: var(--color-primary);
}

.count {
  font-size: 0.8em;
  padding: 2px 8px;
  background: rgba(0, 240, 255, 0.1);
  color: var(--color-primary);
  border-radius: 10px;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.law-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: var(--transition-fast);
  border: 1px solid transparent;
}

.law-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.law-item.active {
  border-color: rgba(0, 240, 255, 0.3);
  background: rgba(0, 240, 255, 0.05);
}

.law-info {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.law-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.95em;
}

.status-icon.active {
  color: var(--color-primary);
}

.status-circle {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-text-muted);
  border-radius: 50%;
  opacity: 0.5;
}

.delete-btn {
  padding: 5px;
  background: transparent;
  color: var(--color-text-muted);
  opacity: 0;
  transition: var(--transition-fast);
}

.law-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff4d4d;
}

.add-law-section {
  padding: 15px;
  border-top: 1px solid var(--glass-border);
  display: flex;
  gap: 10px;
}

.add-law-section input {
  flex: 1;
  background: rgba(0, 0, 0, 0.2);
}

.add-btn {
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-muted);
  font-size: 0.9em;
  font-style: italic;
}
</style>
