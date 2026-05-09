<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/20 backdrop-blur-[2px]" @click.self="close">
        <div class="bg-keGray border border-slate-700/50 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl relative" role="dialog" aria-modal="true">
          
          <button @click="close" class="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>

          <div class="p-6">
             <div class="flex items-center justify-between mb-1">
               <div class="text-xs font-bold uppercase tracking-widest text-keWheat">{{ item.category || 'Unknown Category' }}</div>
               <div v-if="item.expiration_date" class="text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded border border-slate-700/50 flex items-center gap-1">
                 <svg class="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                 {{ formatDate(item.expiration_date) }}
               </div>
             </div>
             <div class="flex items-start justify-between">
               <h2 class="text-2xl font-bold text-slate-100 capitalize">{{ item.name }}</h2>
               <div class="flex flex-col items-end">
                 <button @click.stop.prevent="handleDeleteClick" class="p-1.5 rounded-md transition-colors relative z-10 flex items-center justify-center" :class="isConfirming ? 'bg-red-900 text-red-200 hover:bg-red-800 border border-red-700' : 'text-slate-500 hover:text-red-400 hover:bg-slate-800'" :title="isConfirming ? 'Click again to confirm' : 'Delete Item'">
                   <span v-if="isConfirming" class="text-xs px-2 font-bold uppercase tracking-wider">Sure?</span>
                   <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                 </button>
                 <span v-if="actionError" class="text-[10px] text-red-400 mt-1 max-w-[150px] leading-tight text-right">{{ actionError }}</span>
               </div>
             </div>
             <div class="mt-2 mb-4">
               <button 
                 v-if="receiptDetails" 
                 @click="!receiptDetails.isGhost && navigateToReceipt()"
                 class="group inline-flex items-center text-xs px-3 py-1.5 rounded-full border transition-all"
                 :class="[receiptDetails.isGhost ? 'bg-slate-800/40 border-slate-700/30 text-slate-500 cursor-default' : 'bg-slate-800/80 hover:bg-keBlue/20 text-slate-300 hover:text-keBlue border-slate-700/50 hover:border-keBlue/50 cursor-pointer']"
                 :title="receiptDetails.isGhost ? 'Original receipt has been deleted' : 'View Source Receipt'"
               >
                 <span class="mr-2">{{ receiptDetails.isGhost ? '👻' : '🧾' }}</span>
                 <span class="font-medium mr-1">{{ receiptDetails.store_name }}</span>
                 <span class="opacity-50 mx-1">•</span>
                 <span>{{ formatDate(receiptDetails.scan_date) }}</span>
                 <svg v-if="!receiptDetails.isGhost" class="w-3 h-3 ml-2 opacity-0 group-hover:opacity-100 transition-opacity -rotate-45" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
               </button>
             </div>
             
             <div class="flex flex-col space-y-3">
               
               <div v-if="item.storage_location" class="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                 <span class="text-slate-400">Storage Location:</span>
                 <span class="text-slate-200 font-medium">{{ item.storage_location }}</span>
               </div>
               
               <div v-if="item.added_date && !receiptDetails" class="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                 <span class="text-slate-400">Purchase Date:</span>
                 <span class="text-slate-200">{{ formatDate(item.added_date) }}</span>
               </div>
               
               <div class="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                 <span class="text-slate-400">Available Qty:</span>
                 <span class="text-slate-200 font-mono text-keBlue">{{ formatAmount(item.amount) }} {{ item.unit }}</span>
               </div>
               
               <div class="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                 <span class="text-slate-400">Status:</span>
                 <span :class="freshnessClass" class="font-bold">{{ freshnessText }}</span>
               </div>

             </div>

             <div class="mt-8 flex justify-center">
               <p class="text-[10px] text-slate-500 uppercase tracking-widest text-center max-w-[200px]">Use the Command Hub [Chef's Cognition HUD] to ask for recipes regarding this item.</p>
             </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'
import { useChefFSM } from '../../composables/useChefFSM'

const props = defineProps({
  show: Boolean,
  item: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['close'])

const { isLoading, history, ghostReceipts, getChefAdvice, activeTab, selectedReceipt, deleteItem, fetchFridge, fetchHistory } = useKitchenAPI()
const { updateState } = useChefFSM()

const isConfirming = ref(false)
const actionError = ref(null)

const receiptDetails = computed(() => {
  if (props.item.receipt_id) {
    return history.value.find(r => r.id === props.item.receipt_id) || null
  }
  
  // Try to map a ghost receipt by checking added_date matching scan_date
  if (props.item.added_date && ghostReceipts.value.length) {
     const itemDate = new Date(props.item.added_date).toISOString().split('T')[0]
     const ghost = ghostReceipts.value.find(g => {
        const scanD = new Date(g.scan_date)
        if (isNaN(scanD)) return false
        return scanD.toISOString().split('T')[0] === itemDate
     })
     if (ghost) return { ...ghost, isGhost: true }
  }
  return null
})

const navigateToReceipt = () => {
  if (receiptDetails.value) {
    selectedReceipt.value = receiptDetails.value
    activeTab.value = 'archive'
    close()
  }
}

const handleDeleteClick = async () => {
  actionError.value = null
  if (!props.item || !props.item.id) {
    actionError.value = "Item ID missing."
    return
  }
  
  if (!isConfirming.value) {
    isConfirming.value = true
    setTimeout(() => { isConfirming.value = false }, 3000)
    return
  }

  try {
    isConfirming.value = false
    await deleteItem(props.item.id)
    await Promise.all([fetchFridge(), fetchHistory()])
    emit('close')
  } catch (err) {
    console.error("Delete item failed:", err)
    actionError.value = err.message || "Failed to delete"
  }
}

const close = () => {
    if(!isLoading.value) emit('close')
}

// Global keydown event
const handleKey = (e) => {
  if (e.key === 'Escape' && props.show) close()
}

onMounted(() => window.addEventListener('keydown', handleKey))
onUnmounted(() => window.removeEventListener('keydown', handleKey))

// Removed requestRecipe

const freshnessClass = computed(() => {
  if (props.item.days_left < 0) return 'text-keTerracotta'
  if (props.item.days_left <= 2) return 'text-orange-500'
  return 'text-green-400'
})

const freshnessText = computed(() => {
  if (props.item.days_left < 0) return `Spoiled (${props.item.days_left}d)`
  if (props.item.days_left <= 2) return `Expiring (${props.item.days_left}d)`
  return `Fresh (${props.item.days_left}d)`
})

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown Date'
  const dateObj = new Date(dateString)
  if (isNaN(dateObj.getTime())) return 'Unknown Date'
  return dateObj.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const formatAmount = (amount) => {
  if (amount == null) return ''
  return Number(amount).toString()
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
