<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/20 backdrop-blur-[2px]" @click.self="close">
        <div class="bg-neoGray border border-slate-700/50 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl relative" role="dialog" aria-modal="true">
          
          <button @click="close" class="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>

          <div class="p-6">
             <div class="flex items-center justify-between mb-1">
               <div class="text-xs font-bold uppercase tracking-widest text-neoWheat">{{ item.category || 'Unknown Category' }}</div>
               <div v-if="item.expiration_date" class="text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded border border-slate-700/50 flex items-center gap-1">
                 <svg class="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                 {{ formatDate(item.expiration_date) }}
               </div>
             </div>
             <h2 class="text-2xl font-bold text-slate-100 capitalize">{{ item.name }}</h2>
             <div class="mt-2 mb-4">
               <button 
                 v-if="item.receipt_id && receiptDetails" 
                 @click="navigateToReceipt"
                 class="group inline-flex items-center text-xs px-3 py-1.5 bg-slate-800/80 hover:bg-neoBlue/20 text-slate-300 hover:text-neoBlue rounded-full border border-slate-700/50 hover:border-neoBlue/50 transition-all cursor-pointer"
                 title="View Source Receipt"
               >
                 <span class="mr-2">🧾</span>
                 <span class="font-medium mr-1">{{ receiptDetails.store_name }}</span>
                 <span class="opacity-50 mx-1">•</span>
                 <span>{{ formatDate(receiptDetails.scan_date) }}</span>
                 <svg class="w-3 h-3 ml-2 opacity-0 group-hover:opacity-100 transition-opacity -rotate-45" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
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
                 <span class="text-slate-200 font-mono text-neoBlue">{{ formatAmount(item.amount) }} {{ item.unit }}</span>
               </div>
               
               <div class="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                 <span class="text-slate-400">Status:</span>
                 <span :class="freshnessClass" class="font-bold">{{ freshnessText }}</span>
               </div>

             </div>

             <div class="mt-8 flex justify-center">
               <button 
                 @click="requestRecipe"
                 :disabled="isLoading"
                 class="w-full bg-neoWheat hover:bg-yellow-400 active:bg-yellow-500 text-slate-900 font-bold py-3 px-4 rounded-xl shadow-lg transition-all flex justify-center items-center gap-2 transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
               >
                  <svg v-if="isLoading" class="animate-spin h-5 w-5 text-slate-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  <span v-if="!isLoading">🔥 Ask Chef for a Recipe</span>
                  <span v-else>Cooking...</span>
               </button>
             </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'
import { useChefFSM } from '../../composables/useChefFSM'

const props = defineProps({
  show: Boolean,
  item: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['close'])

const { isLoading, history, getChefAdvice, activeTab, selectedReceipt } = useKitchenAPI()
const { updateState } = useChefFSM()

const receiptDetails = computed(() => {
  if (!props.item.receipt_id) return null
  return history.value.find(r => r.id === props.item.receipt_id) || null
})

const navigateToReceipt = () => {
  if (receiptDetails.value) {
    selectedReceipt.value = receiptDetails.value
    activeTab.value = 'archive'
    close()
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

const requestRecipe = async () => {
  try {
    const data = await getChefAdvice(props.item.name)
    updateState(data)
    close()
  } catch (e) {
    console.error(e)
    // The FSM error state is managed in InteractionZone generally,
    // but here we just safely close so the interaction zone shows the banner
    close()
  }
}

const freshnessClass = computed(() => {
  if (props.item.days_left < 0) return 'text-neoTerracotta'
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
