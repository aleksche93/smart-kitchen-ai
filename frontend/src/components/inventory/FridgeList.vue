<template>
  <Card title="Fridge Inventory" class="h-full">
    <div v-if="isLoading" class="text-slate-400 flex justify-center py-10 animate-pulse">
      Scanning sensors...
    </div>
    <div v-else-if="error" class="text-red-400">
      Error: {{ error }}
    </div>
    
    <div v-else-if="items.length === 0" class="flex flex-col items-center justify-center p-12 text-slate-500 space-y-4 opacity-50">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 stroke-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <h3 class="text-lg font-medium">Fridge is empty</h3>
      <p class="text-sm text-center">Scan a receipt to start adding inventory.</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
      <div 
        v-for="item in items" 
        :key="item.name"
        @click="selectItem(item)"
        class="group p-4 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-neoGray hover:border-neoBlue shadow-sm cursor-pointer transition-all flex flex-col justify-between h-full hover:-translate-y-0.5"
      >
        <div class="flex justify-between items-start mb-2">
          <span class="block font-bold text-slate-100 group-hover:text-neoBlue transition-colors text-lg capitalize">{{ item.name }}</span>
          <!-- Status Badges -->
          <span 
            v-if="item.days_left < 0" 
            class="px-2.5 py-1 text-[10px] uppercase font-bold rounded-md bg-red-900 text-red-300 border border-red-700 shadow-[0_0_8px_rgba(239,68,68,0.4)]"
          >
            ☣️ Spoiled
          </span>
          <span 
            v-else-if="item.days_left <= 2" 
            class="px-2.5 py-1 text-[10px] uppercase font-bold rounded-md bg-yellow-900/60 text-neoYellow border border-yellow-700/50 shadow-[0_0_8px_rgba(250,204,21,0.2)]"
          >
            ⚠️ Expiring
          </span>
          <span 
            v-else 
            class="px-2.5 py-1 text-[10px] uppercase font-bold rounded-md bg-slate-700 text-slate-300 border border-slate-600"
          >
            Fresh
          </span>
        </div>
        
        <div class="flex justify-between items-end border-t border-slate-700/50 pt-2 mt-2">
          <span class="text-xs font-mono text-neoBlue bg-neoBlue/10 px-2 py-0.5 rounded">{{ item.amount }} {{ item.unit }}</span>
          <div class="text-right">
             <span class="block text-[10px] text-slate-500 uppercase tracking-widest font-semibold">{{ item.category }}</span>
             <span class="text-xs font-medium text-slate-400">{{ item.days_left < 0 ? 'Expired' : item.days_left + ' days left' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Teleport Modal -->
    <ItemModal :show="showModal" :item="activeItem" @close="showModal = false" />
  </Card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Card from '../ui/Card.vue'
import ItemModal from './ItemModal.vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'

const items = ref([])
const showModal = ref(false)
const activeItem = ref({})

const { isLoading, error, fetchFridge } = useKitchenAPI()

const loadData = async () => {
  items.value = await fetchFridge()
}

const selectItem = (item) => {
  activeItem.value = item
  showModal.value = true
}

onMounted(loadData)
</script>
