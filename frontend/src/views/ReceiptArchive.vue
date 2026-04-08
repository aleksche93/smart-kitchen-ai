<template>
  <div class="h-full pt-2 flex flex-col relative w-full pr-2">
    <!-- Header -->
    <div class="flex justify-between items-end border-b border-slate-700/50 pb-4 mb-6">
      <div>
        <h2 class="text-3xl font-bold text-slate-100 mb-1">Receipt Archive</h2>
        <p class="text-sm text-slate-400">View and manage history of digitized grocery scans.</p>
      </div>
      <button @click="refresh" :disabled="isLoading" class="text-neoBlue hover:text-blue-400 flex items-center text-sm font-medium transition-colors">
        <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
        Sync
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="history.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-20 px-4 text-slate-500 space-y-4 opacity-80 border-2 border-dashed border-slate-700/50 rounded-2xl mx-2 bg-slate-800/20">
      <div class="bg-slate-800 p-4 rounded-full shadow-inner mb-2">
        <svg class="h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h3 class="text-xl font-bold text-slate-300">Archive Empty</h3>
      <p class="text-sm text-center max-w-sm">No receipts have been digitized yet. Scan your grocery receipts to populate your archive and track expenses.</p>
    </div>

    <!-- Grid Layout -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12">
      <div 
        v-for="receipt in history" 
        :key="receipt.id"
        class="bg-slate-800 border border-slate-700/50 rounded-2xl overflow-hidden shadow-lg transition-transform hover:-translate-y-1 hover:border-slate-500 flex flex-col group cursor-pointer"
        @click="openModal(receipt)"
      >
        <!-- Thumbnail wrapper -->
        <div class="h-40 w-full overflow-hidden bg-slate-900 border-b border-slate-700 relative flex items-center justify-center">
          <img 
            :src="'http://localhost:8000/images/' + extractFilename(receipt.image_path)" 
            class="w-20 h-20 object-cover rounded-xl shadow-lg border border-slate-600/50"
            @error="onImageError"
            alt="Receipt Scan"
          />
          <div class="absolute bottom-3 left-3 flex flex-col items-center justify-center bg-slate-900/80 rounded-full px-3 py-1">
            <span class="text-neoWheat font-bold text-xs">{{ receipt.added_items_count }} Items</span>
          </div>
        </div>
        
        <!-- Metadata -->
        <div class="p-4 flex flex-col space-y-3 flex-1 relative">
           <button @click.stop="handleDelete(receipt.id)" class="absolute top-4 right-4 text-slate-500 hover:text-neoTerracotta transition-colors bg-slate-800 p-1 rounded-full shadow-inner" title="Delete Receipt">
             <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
           </button>

           <div class="flex flex-col">
             <span class="text-sm font-bold text-slate-100 truncate pr-6">{{ receipt.store_name }}</span>
             <span class="text-xs text-slate-400 mt-1">{{ formatDate(receipt.scan_date) }}</span>
           </div>

           <div class="flex flex-col flex-1 justify-end">
             <span class="text-lg font-mono text-neoBlue font-bold block pt-2 border-t border-slate-700/50">
               {{ receipt.total_price != null ? `${receipt.total_price.toFixed(2)} ${receipt.currency}` : 'Completed' }}
             </span>
           </div>
        </div>
      </div>
    </div>

    <!-- Lightbox Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="selectedReceipt" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm p-4" @click.self="selectedReceipt = null">
          <div 
             class="bg-neoGray border border-slate-700/50 rounded-2xl w-full overflow-hidden shadow-2xl relative flex flex-col transition-all duration-500 ease-in-out"
             :class="isExpanded ? 'max-w-6xl lg:flex-row h-[90vh]' : 'max-w-3xl flex-col max-h-[85vh]'"
          >
            
            <button @click="selectedReceipt = null" class="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors z-20 bg-slate-900/50 p-1 rounded-full backdrop-blur-sm shadow-md">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>

            <!-- Expanded Left Panel (Full Image) -->
            <div 
               class="transition-all duration-500 ease-in-out bg-black/90 flex flex-col items-center justify-center shrink-0 relative cursor-zoom-out"
               :class="isExpanded ? 'lg:w-[40%] h-64 lg:h-full opacity-100 border-b lg:border-b-0 lg:border-r border-slate-700/50 p-4' : 'w-0 h-0 opacity-0 overflow-hidden border-none p-0'"
               @click="isExpanded = false"
               title="Click to collapse"
            >
               <img v-if="isExpanded" :src="'http://localhost:8000/images/' + extractFilename(selectedReceipt.image_path)" class="w-full h-full object-cover rounded drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]" alt="Full Receipt" />
               <div v-if="isExpanded" class="absolute bottom-4 left-0 right-0 text-center text-slate-100 bg-black/50 py-1 text-xs font-mono uppercase tracking-widest pointer-events-none transition-opacity hover:opacity-0">
                 Click anywhere to collapse
               </div>
            </div>

            <!-- Main Data Panel (Right side if expanded) -->
            <div 
               class="flex flex-col transition-all duration-500 ease-in-out overflow-hidden"
               :class="isExpanded ? 'lg:w-[60%] h-full' : 'w-full max-h-[85vh]'"
            >
              <!-- Header -->
              <div class="p-6 border-b border-slate-700/50 bg-slate-800/80 flex justify-between items-start gap-4 shrink-0 transition-all">
                 <div class="flex flex-col flex-1">
                   <h3 class="text-2xl font-bold text-slate-100 mb-1 pr-8">Receipt from {{ selectedReceipt.store_name }}</h3>
                   <p class="text-sm text-slate-400 mb-3">{{ formatDate(selectedReceipt.scan_date) }}</p>
                   
                   <!-- Maps Badge Pill -->
                   <div v-if="selectedReceipt.comment" class="inline-flex w-max items-center bg-neoBlue/10 border border-neoBlue/30 text-neoBlue rounded-full px-3 py-1 shadow-sm hover:bg-neoBlue/20 transition-colors">
                     <svg class="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                     <a :href="`https://maps.google.com/?q=${encodeURIComponent(selectedReceipt.comment)}`" target="_blank" class="text-xs font-medium truncate max-w-[200px]">
                       {{ selectedReceipt.comment }}
                     </a>
                   </div>
                 </div>
                 
                 <!-- Thumbnail inside Header (Only visible if NOT expanded) -->
                 <div v-show="!isExpanded" class="relative group cursor-zoom-in w-24 h-24 shrink-0 rounded-xl overflow-hidden border border-slate-600 shadow-md transition-all">
                   <img :src="'http://localhost:8000/images/' + extractFilename(selectedReceipt.image_path)" class="w-full h-full object-cover" alt="Thumb" @error="onImageError" />
                   <div @click="isExpanded = true" class="absolute inset-0 bg-slate-900/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-[2px]">
                     <span class="text-2xl drop-shadow-md">🔍</span>
                   </div>
                 </div>
              </div>

            <!-- Scrollable Table Body -->
            <div class="p-6 flex-1 overflow-y-auto custom-scrollbar bg-slate-800 max-h-[50vh]">
               <div v-if="!selectedReceipt.added_items || selectedReceipt.added_items.length === 0" class="text-slate-500 italic text-sm text-center py-8">
                 No items digitized.
               </div>
               
               <table v-else class="w-full text-left text-sm text-slate-300">
                  <thead class="text-xs uppercase bg-slate-700/50 text-slate-400 sticky top-0">
                    <tr>
                      <th class="px-3 py-2 rounded-tl-lg font-semibold">Product</th>
                      <th class="px-3 py-2 font-semibold">Qty/Unit</th>
                      <th class="px-3 py-2 font-semibold">Unit Price</th>
                      <th class="px-3 py-2 rounded-tr-lg font-semibold text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-700/30">
                    <tr v-for="item in selectedReceipt.added_items" :key="item.id" class="hover:bg-slate-700/20 transition-colors">
                      <td class="px-3 py-2.5 font-medium capitalize text-slate-200">
                         <div class="flex items-center space-x-1.5">
                           <span>{{ item.name }}</span>
                           <span v-if="item.is_packaged" title="Packaged Item">📦</span>
                         </div>
                         <div v-if="item.brand" class="text-[10px] text-slate-500 font-mono uppercase mt-0.5 tracking-wider">{{ item.brand }}</div>
                      </td>
                      <td class="px-3 py-2.5 text-slate-400">{{ formatAmount(item.amount) }} <span class="text-xs opacity-70">{{ item.unit }}</span></td>
                      <td class="px-3 py-2.5 font-mono text-[11px] text-slate-400">
                        {{ item.unit_price ? item.unit_price.toFixed(2) : '-' }}
                      </td>
                      <td class="px-3 py-2.5 text-right font-mono text-neoBlue font-medium">
                        {{ item.row_subtotal ? item.row_subtotal.toFixed(2) : '-' }}
                      </td>
                    </tr>
                  </tbody>
               </table>
            </div>

            <!-- Footer Totals -->
            <div class="p-6 bg-slate-900 border-t border-slate-700 flex justify-between items-center shrink-0">
               <div class="text-sm text-slate-400 flex flex-col">
                  <span>{{ selectedReceipt.added_items_count }} items processed</span>
               </div>
               <div class="flex items-center gap-4">
                  <div class="text-sm text-slate-400 uppercase tracking-widest">Grand Total</div>
                  <div class="text-2xl font-mono text-neoBlue font-bold bg-neoBlue/10 px-4 py-1.5 rounded-lg border border-neoBlue/30 shadow-[0_0_15px_rgba(59,130,246,0.15)]">
                    {{ selectedReceipt.total_price != null ? `${selectedReceipt.total_price.toFixed(2)} ${selectedReceipt.currency}` : 'N/A' }}
                  </div>
               </div>
            </div>

            </div> <!-- End Right Panel -->
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useKitchenAPI } from '../composables/useKitchenAPI'

const { isLoading, history, fetchHistory, deleteReceipt, selectedReceipt } = useKitchenAPI()

const isExpanded = ref(false)

// Handle ESC key for lightbox
const handleKeydown = (e) => {
  if (e.key === 'Escape' && selectedReceipt.value) {
    selectedReceipt.value = null
    isExpanded.value = false
  }
}

onMounted(() => {
  if (history.value.length === 0) fetchHistory()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

const refresh = () => fetchHistory()

const extractFilename = (path) => {
  if (!path) return 'missing.jpg'
  // Handle windows or unix slashes
  return path.split(/[\\/]/).pop()
}

const onImageError = (e) => {
  e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="%231e293b" width="100" height="100"/><text x="50" y="50" font-family="sans-serif" font-size="10" fill="%2364748b" text-anchor="middle" dominant-baseline="middle">Missing Image</text></svg>'
}

const openModal = (receipt) => {
  isExpanded.value = false
  selectedReceipt.value = receipt
}

const handleDelete = async (id) => {
  const isConfirm = window.confirm("Are you sure you want to delete this receipt and ALL its synchronized items from your fridge?")
  if (!isConfirm) return
  try {
    await deleteReceipt(id)
    if (selectedReceipt.value && selectedReceipt.value.id === id) {
      selectedReceipt.value = null
      isExpanded.value = false
    }
  } catch (e) {
    alert("Failed to delete the receipt. See console for details.")
    console.error(e)
  }
}

// Strict UI Date Format Rule: "Month Day, Year"
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
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
