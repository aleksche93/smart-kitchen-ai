<template>
  <div class="flex flex-col h-full bg-transparent overflow-hidden space-y-0 relative pb-2 pt-1 font-sans">
    
    <!-- Top Area: Actions Bar -->
    <div class="flex justify-between items-center bg-slate-800/80 px-4 py-2 flex-shrink-0 border border-slate-700/50 rounded-lg mb-3">
      <div class="flex items-center gap-4">
        <!-- Scan Receipt File Picker -->
        <label class="cursor-pointer text-xs uppercase tracking-wider font-bold text-slate-300 hover:text-neoYellow transition-colors flex items-center group" title="Scan Receipt / Vision">
          <svg class="w-4 h-4 mr-1.5 opacity-70 group-hover:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          Scan Receipt
          <input type="file" accept="image/*" class="hidden" @change="handleFileUpload" />
        </label>
        <!-- Clear Session -->
        <button @click="handleClearSession" class="text-xs uppercase tracking-wider font-bold text-slate-400 hover:text-red-400 transition-colors flex items-center group">
          <svg class="w-4 h-4 mr-1.5 opacity-70 group-hover:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          Clear Session
        </button>
      </div>

      <!-- Toggle HUD -->
      <button 
        @click="isConsoleOpen = !isConsoleOpen"
        class="text-slate-500 hover:text-neoBlue transition-colors block"
        title="Toggle HUD Console"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
      </button>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="bg-red-900/40 border border-red-700 text-red-300 text-sm p-3 rounded-lg flex items-start animate-pulse flex-shrink-0 mb-3">
      <span class="mr-2">⚠️</span>
      <p>{{ error }}</p>
    </div>
    <!-- Success Banner -->
    <div v-if="successMsg" class="bg-green-900/40 border border-green-700 text-green-300 text-sm p-3 rounded-lg flex items-start transition-all flex-shrink-0 mb-3">
      <p>{{ successMsg }}</p>
    </div>

    <!-- Middle Area (Scrollable Message History) -->
    <div class="flex-grow overflow-y-auto p-4 custom-scrollbar flex flex-col space-y-4 w-full bg-slate-800/30 rounded-lg min-h-0 mb-3" ref="chatContainer">
       <div v-for="(msg, index) in chatHistory" :key="index"
            :class="msg.role === 'user' ? 'self-end bg-neoBlue/20 text-neoBlue px-4 py-2 rounded-2xl rounded-tr-sm max-w-[85%] break-words shadow-sm text-sm border border-neoBlue/30' : 'self-start bg-slate-800/80 text-slate-300 px-4 py-3 rounded-2xl rounded-tl-sm max-w-[85%] shadow-md text-sm border border-slate-700/50 flex flex-col space-y-2'">
          <span>{{ msg.content }}</span>
          <button v-if="msg.role === 'assistant' && index === chatHistory.length - 1 && chefState.showMagicTrigger" @click="executeMagic()" class="self-start mt-1 px-3 py-1.5 bg-neoYellow/10 hover:bg-neoYellow/20 text-neoYellow border border-neoYellow/30 rounded-full text-xs font-bold uppercase tracking-wider transition-all transform hover:scale-105 animate-fade-in-up flex items-center shadow-[0_0_10px_rgba(250,204,21,0.1)]">
             ✨ Generate Magic
          </button>
       </div>
    </div>

    <!-- Bottom Area: Chat Input Space -->
    <div class="flex flex-col flex-shrink-0 mt-auto space-y-2">
      <!-- Thought Ticker Terminal (Anchored directly above input when open) -->
      <div v-show="isConsoleOpen" :class="[lastQuery || chefState.chatMessage ? 'h-32' : 'flex-1 min-h-[120px]']" class="rounded-xl border border-slate-700/50 bg-slate-900/60 backdrop-blur-md shadow-inner overflow-hidden relative transition-all duration-500 w-full shrink-0">
        <ThoughtTicker />
      </div>

      <div class="flex space-x-2">
        <div class="relative flex-1">
          <input 
            v-model="localInput"
            type="text" 
            placeholder="Ask Chef..."
            class="w-full bg-slate-900/50 border border-slate-600 focus:border-neoBlue focus:ring-1 focus:ring-neoBlue text-slate-200 rounded-full py-3 pl-5 pr-5 outline-none transition-all shadow-inner"
            @keyup.enter="handleAdvice"
          />
        </div>
        <button 
          @click="handleAdvice"
          :disabled="btnState === BUTTON_STATES.ACTIVE || !localInput.trim()"
          class="w-[100px] bg-neoBlue hover:bg-blue-600 active:bg-blue-700 text-white font-medium rounded-full transition-all duration-300 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed shrink-0 shadow-md"
        >
          <span v-if="btnState === BUTTON_STATES.IDLE" class="text-sm">Send</span>
          <span v-else class="flex items-center text-xs whitespace-nowrap">
            <span class="mr-1 animate-pulse">{{ processingAction.icon }}</span>
            {{ processingAction.text }}
          </span>
        </button>
      </div>
    </div>

    <!-- Dynamic Receipt Output -->
    <ScannedReceiptOutput 
      v-if="scannedItems.length" 
      :items="scannedItems" 
      @clear="scannedItems = []" 
    />



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
import { useI18n } from '../../plugins/i18n'
import { useChefStore } from '../../stores/chefStore'
import { onMounted, nextTick } from 'vue'

const { t } = useI18n()
const chefStore = useChefStore()
const { isLoading, error, getChefAdvice, sendChatStream, scanReceipt, fetchFridge, fetchSessionHistory, clearSession } = useKitchenAPI()
const { updateState, resetState } = useChefFSM()

const chatHistory = ref([])
const chatContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

onMounted(async () => {
  const historyData = await fetchSessionHistory()
  if (historyData && historyData.messages) {
    chatHistory.value = historyData.messages
    scrollToBottom()
  }
})

const localInput = ref('')
const scannedItems = ref([])
const successMsg = ref(null)
const isConsoleOpen = ref(true)
const lastQuery = ref(null)


const BUTTON_STATES = {
  IDLE: 'IDLE',
  ACTIVE: 'ACTIVE'
}
const btnState = ref(BUTTON_STATES.IDLE)

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

const handleClearSession = async () => {
  await clearSession()
  chatHistory.value = []
  lastQuery.value = null
  chefState.chatMessage = ''
  chefState.showMagicTrigger = false
}

const handleAdvice = async () => {
  if (!localInput.value.trim() || btnState.value === BUTTON_STATES.ACTIVE) return
  error.value = null

  // Intent Triage
  const lower = localInput.value.toLowerCase()
  const intents = ['recipe', 'generate', 'ідеї', 'рецепт', 'cook', 'приготувати', 'смачне']
  if (intents.some(i => lower.includes(i))) {
    lastQuery.value = localInput.value
    chefState.chatMessage = t('intents.magic_trigger_message')
    chefState.showMagicTrigger = true
    chefState.emotionDisplay = 'PLAYFUL'
    localInput.value = ''
    return
  }

  // Flow A: Plain Chat
  btnState.value = BUTTON_STATES.ACTIVE
  const queryToSent = localInput.value
  lastQuery.value = queryToSent
  localInput.value = ''

  chatHistory.value.push({ role: 'user', content: queryToSent })
  chatHistory.value.push({ role: 'assistant', content: '' }) // Empty placeholder for stream
  scrollToBottom()

  try {
    await sendChatStream(
      queryToSent,
      (textChunk) => {
        // Append chunk to the last assistant message
        const lastMsg = chatHistory.value[chatHistory.value.length - 1]
        lastMsg.content += textChunk
        scrollToBottom()
      },
      (emotion) => {
        chefState.emotionDisplay = emotion
        chefStore.setEmotion(emotion)
      },
      (errMsg) => {
        error.value = "Сhef error: " + errMsg
        chefState.emotionDisplay = 'ANGRY'
      }
    )
  } catch (err) {
    error.value = "Сhef refused to chat: " + (err.message || 'Connection lost.')
    chefState.emotionDisplay = 'ANGRY'
  } finally {
    btnState.value = BUTTON_STATES.IDLE
  }
}

const executeMagic = async (query = lastQuery.value) => {
  if (btnState.value === BUTTON_STATES.ACTIVE) return
  error.value = null
  btnState.value = BUTTON_STATES.ACTIVE
  chefState.showMagicTrigger = false
  
  try {
    if (query !== lastQuery.value) {
      lastQuery.value = query
    }
    const data = await getChefAdvice(query)
    updateState(data)
    localInput.value = ''
  } catch (err) {
    error.value = "Сhef refused to answer: " + (err.message || 'Connection lost.')
    chefState.emotionDisplay = 'ANGRY'
  } finally {
    btnState.value = BUTTON_STATES.IDLE
  }
}

const rawImageObject = ref(null)

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (file.size > 5 * 1024 * 1024) { // 5MB limit
    error.value = t('errors.file_too_large')
    event.target.value = ''
    return
  }
  error.value = null
  
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
  
  chefStore.logThought(t('ticker.checking_traps'))
  chefStore.logThought(t('ticker.processing'))
  
  try {
    const data = await scanReceipt(fileToUpload)
    if (data.items_added) {
      chefStore.logThought(t('ticker.identified_shop', { shop: data.store_name || 'Unknown' }))
      chefStore.logThought(t('ticker.extracted_items', { count: data.total_recognized }))
      
      scannedItems.value = data.items_added 
      successMsg.value = t('scan.success', { store: data.store_name || 'Unknown', count: data.total_recognized })
      setTimeout(() => { successMsg.value = null }, 5000)
      
      const hasBag = data.items_added.some(item => item.is_bag)
      if (hasBag) {
        chefState.chatMessage = t('scan.bag_detected')
      } else {
        chefState.chatMessage = t('scan.no_bag')
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
    // Check if error is Duplicate Receipt (409)
    if (err.message && err.message.toLowerCase().includes('duplicate')) {
       error.value = t('errors.duplicate_receipt')
       chefState.emotionDisplay = "ANGRY"
       fetchFridge() // Silent refresh of the fridge on duplicate
    } else {
       error.value = err.message || 'Connection lost.'
    }
  }
}
</script>
