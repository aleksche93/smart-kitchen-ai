<template>
  <div class="mt-8 flex flex-col space-y-4">
    <!-- Chat Input Area -->
    <div class="flex space-x-2">
      <input 
        v-model="localInput"
        type="text" 
        placeholder="Enter ingredient or ask Chef..."
        class="flex-1 bg-slate-900/50 border border-slate-600 focus:border-neoBlue focus:ring-1 focus:ring-neoBlue text-slate-200 rounded-lg py-3 px-4 outline-none transition-all shadow-inner"
        @keyup.enter="handleAdvice"
      />
      <button 
        @click="handleAdvice"
        :disabled="isLoading || !localInput.trim()"
        class="w-32 bg-neoBlue hover:bg-blue-600 active:bg-blue-700 text-white font-medium rounded-lg transition-all flex items-center justify-center shadow-[0_0_10px_rgba(59,130,246,0.3)] hover:shadow-[0_0_15px_rgba(59,130,246,0.5)] disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="isLoading" class="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span v-if="!isLoading">Send ></span>
        <span v-else class="flex items-center">
          <span class="mr-2 animate-pulse">{{ processingAction.icon }}</span>
          {{ processingAction.text }}...
        </span>
      </button>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="bg-red-900/40 border border-red-700 text-red-300 text-sm p-3 rounded-lg flex items-start animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.3)]">
      <span class="mr-2">⚠️</span>
      <p>{{ error }}</p>
    </div>

    <!-- Success Banner -->
    <div v-if="successMsg" class="bg-green-900/40 border border-green-700 text-green-300 text-sm p-3 rounded-lg flex items-start shadow-[0_0_15px_rgba(34,197,94,0.3)] transition-all">
      <p>{{ successMsg }}</p>
    </div>

    <!-- Scanner & Controls -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between border-t border-slate-700/50 pt-4 mt-2 gap-4">
      <div class="flex items-center space-x-4">
          <span class="text-xs text-slate-500 tracking-wider uppercase">Actions</span>
          <label class="cursor-pointer px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-md text-sm text-neoYellow transition-colors flex items-center shadow-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span>Scan Receipt</span>
            <input type="file" accept="image/*" class="hidden" @change="handleFileUpload" />
          </label>
      </div>
      
      <button 
        @click="handleReset"
        class="px-4 py-2 bg-slate-800 hover:bg-red-900/50 border border-slate-600 hover:border-red-700/50 rounded-md text-sm text-slate-400 hover:text-red-300 transition-colors flex items-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Reset Session
      </button>
    </div>

    <!-- Dynamic Receipt Output -->
    <ScannedReceiptOutput 
      v-if="scannedItems.length" 
      :items="scannedItems" 
      @clear="scannedItems = []" 
    />

    <!-- Thought Ticker Log Stream -->
    <ThoughtTicker />

    <!-- Hybrid Cropper Teleport -->
    <Teleport to="body">
      <HybridCropper 
         v-if="rawImageObject"
         :image-url="rawImageObject"
         @crop="handleCroppedImage"
         @cancel="cancelCrop"
      />
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'
import { useChefFSM, chefState } from '../../composables/useChefFSM'
import ScannedReceiptOutput from './ScannedReceiptOutput.vue'
import HybridCropper from '../vision/HybridCropper.vue'
import ThoughtTicker from './ThoughtTicker.vue'

const { isLoading, error, getChefAdvice, scanReceipt } = useKitchenAPI()
const { updateState, resetState } = useChefFSM()

const localInput = ref('')
const scannedItems = ref([])
const successMsg = ref(null)

const processingAction = computed(() => {
   const lower = localInput.value.toLowerCase()
   if (lower.includes('tomato') || lower.includes('vegetable') || lower.includes('potato') || lower.includes('onion') || lower.includes('carrot') || lower.includes('garlic')) {
      return { text: "Chopping veg", icon: "🔪" }
   }
   if (lower.includes('water') || lower.includes('juice') || lower.includes('beer') || lower.includes('wine') || lower.includes('drink') || lower.includes('milk')) {
      return { text: "Pouring drinks", icon: "🫗" }
   }
   if (lower.includes('meat') || lower.includes('chicken') || lower.includes('beef') || lower.includes('pork')) {
      return { text: "Searing meat", icon: "🥩" }
   }
   return { text: "Heating pans", icon: "🍳" }
})

const handleReset = () => {
    resetState()
    localInput.value = ''
    error.value = null
    successMsg.value = null
    scannedItems.value = []
}

const handleAdvice = async () => {
  if (!localInput.value.trim()) return
  error.value = null
  try {
    const data = await getChefAdvice(localInput.value)
    updateState(data)
    localInput.value = '' // Clear input after successful send
  } catch (err) {
    // API failure handled gracefully
    error.value = "Сhef refused to answer: " + (err.message || 'Connection lost.')
    chefState.emotionDisplay = 'ANGRY'
  }
}

const rawImageObject = ref(null)

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Set up raw image for HybridCropper to process 
  rawImageObject.value = URL.createObjectURL(file)
  event.target.value = '' // Reset file input
}

const cancelCrop = () => {
  if (rawImageObject.value) {
    URL.revokeObjectURL(rawImageObject.value)
    rawImageObject.value = null
  }
}

const handleCroppedImage = async (blob) => {
  cancelCrop() // Clears the dialog and securely dismisses original blob memory
  
  error.value = null
  successMsg.value = null
  scannedItems.value = []
  
  // Package Blob explicitly as receipt.jpg per API requirement
  const fileToUpload = new File([blob], "receipt_cropped.jpg", { type: "image/jpeg" })
  
  try {
    const data = await scanReceipt(fileToUpload)
    if (data.items_added) {
      scannedItems.value = data.items_added 
      successMsg.value = `✅ Receipt processed! Store: ${data.store_name || 'Unknown'}. Added ${data.total_recognized} items.`
      setTimeout(() => { successMsg.value = null }, 5000)
      
      const hasBag = data.items_added.some(item => item.is_bag)
      if (hasBag) {
        chefState.adviceText = "I have successfully processed your cropped receipt. Oh, Chef detected a bag! Moving it to your stash... Fun Module activated!"
      } else {
        chefState.adviceText = "I have successfully processed your cropped receipt and updated the fridge inventory! Check the Left Panel. Anything else you want to cook with?"
      }
    } else if (data.items) {
      scannedItems.value = data.items
    } else if (Array.isArray(data)) {
      scannedItems.value = data
    } else {
      scannedItems.value = [data]
    }
    chefState.emotionDisplay = "FOCUSED"
  } catch (err) {
    // API throws errors appropriately
  }
}
</script>
