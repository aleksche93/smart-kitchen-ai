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
       <div v-for="(msg, index) in chatHistory" :key="msg._id || index"
            :class="msg.role === 'user'
              ? 'self-end bg-neoBlue/20 text-neoBlue px-4 py-2 rounded-2xl rounded-tr-sm max-w-[85%] break-words shadow-sm text-sm border border-neoBlue/30'
              : 'self-start bg-slate-800/80 text-slate-300 px-4 py-3 rounded-2xl rounded-tl-sm max-w-[85%] shadow-md text-sm border border-slate-700/50 flex flex-col space-y-2'">
          <!-- Typing indicator: 3 dots — visible ONLY before first chunk arrives -->
          <span v-if="msg.role === 'assistant' && msg.content === '' && isStreaming" class="flex items-center gap-1 py-0.5">
            <span class="w-2 h-2 bg-neoBlue rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-neoBlue rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-neoBlue rounded-full animate-bounce" style="animation-delay: 300ms"></span>
          </span>
          <!-- Content: renders as text arrives chunk by chunk (kinetic typing via SSE) -->
          <span v-else class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}<span
            v-if="msg.role === 'assistant' && isStreaming && index === chatHistory.length - 1 && msg.content !== ''"
            class="inline-block w-0.5 h-3.5 bg-neoBlue ml-0.5 align-middle animate-pulse"
          ></span></span>
          <!-- Magic artifact trigger button — з'являється коли Шеф додає [ACTION: MAGIC_TRIGGER] -->
          <button v-if="msg.role === 'assistant' && index === chatHistory.length - 1 && showMagicButton" @click="executeMagic()" class="self-start mt-1 px-3 py-1.5 bg-neoYellow/10 hover:bg-neoYellow/20 text-neoYellow border border-neoYellow/30 rounded-full text-xs font-bold uppercase tracking-wider transition-all transform hover:scale-105 animate-fade-in-up flex items-center shadow-[0_0_10px_rgba(250,204,21,0.1)]">
             ✨ Generate Magic
          </button>
       </div>
    </div>

    <!-- Bottom Area: Chat Input Space -->
    <div class="flex flex-col flex-shrink-0 mt-auto space-y-2">


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
import { ref, computed } from 'vue'
import { onMounted, nextTick } from 'vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'
import { useChefFSM, chefState } from '../../composables/useChefFSM'
import { useTypewriter } from '../../composables/useTypewriter'
import ScannedReceiptOutput from './ScannedReceiptOutput.vue'
import HybridCropper from '../vision/HybridCropper.vue'
import { useI18n } from '../../plugins/i18n'
import { useChefStore } from '../../stores/chefStore'

const { t } = useI18n()
const chefStore = useChefStore()
const { isLoading, error, getChefAdvice, sendChatStream, scanReceipt, fetchFridge, fetchSessionHistory, clearSession, generateArtifact } = useKitchenAPI()
const { updateState } = useChefFSM()

// Typewriter composable — Variant A (real-time per-chunk typing)
const { type: typeWord } = useTypewriter()

const chatHistory = ref([])
const chatContainer = ref(null)
const isStreaming = ref(false)
let _scrollRAF = null

const scrollToBottom = () => {
  if (_scrollRAF) cancelAnimationFrame(_scrollRAF)
  _scrollRAF = requestAnimationFrame(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

onMounted(async () => {
  const historyData = await fetchSessionHistory()
  if (historyData && historyData.messages) {
    chatHistory.value = historyData.messages.map((m, i) => ({ ...m, _id: 'h_' + i }))
    await nextTick()
    scrollToBottom()
  }
})

const localInput = ref('')
const scannedItems = ref([])
const successMsg = ref(null)
const lastQuery = ref(null)
let _msgCounter = 0

// --- Phase 12.1-B: Magic Trigger Bridge ---
const MAGIC_TAG = '[ACTION: MAGIC_TRIGGER]'
const showMagicButton = ref(false)
const emit = defineEmits(['artifact'])


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
  showMagicButton.value = false
}

const handleAdvice = async () => {
  if (!localInput.value.trim() || btnState.value === BUTTON_STATES.ACTIVE) return
  error.value = null

  // Flow A: Plain Chat
  btnState.value = BUTTON_STATES.ACTIVE
  isStreaming.value = true
  const queryToSent = localInput.value
  lastQuery.value = queryToSent
  localInput.value = ''

  const userMsgId = 'msg_' + (++_msgCounter)
  const assistantMsgId = 'msg_' + (++_msgCounter)
  chatHistory.value = [...chatHistory.value, { role: 'user', content: queryToSent, _id: userMsgId }]
  chatHistory.value = [...chatHistory.value, { role: 'assistant', content: '', _id: assistantMsgId }]
  scrollToBottom()
  let _accumulatedText = ''

  try {
    const TAG_LENGTH = MAGIC_TAG.length
    const _sleep = (ms) => new Promise(r => setTimeout(r, ms))

    await sendChatStream(
      queryToSent,
      async (textChunk) => {
        _accumulatedText += textChunk

        // 1. Повний тег знайдено — strip і активуємо кнопку
        if (_accumulatedText.includes(MAGIC_TAG)) {
          _accumulatedText = _accumulatedText.replace(MAGIC_TAG, '')
          if (!showMagicButton.value) showMagicButton.value = true
        }

        // 2. Tail Buffer: відсікаємо хвіст що може бути початком тегу
        //    "[ACTION" — суфікс, що потенційно стане повним тегом у наступному chunk
        let safeText = _accumulatedText
        const tail = _accumulatedText.slice(-TAG_LENGTH)
        const bracketIdx = tail.lastIndexOf('[')
        if (bracketIdx >= 0) {
          const possiblePartial = tail.slice(bracketIdx)
          // Якщо MAGIC_TAG починається з цього partial — буферизуємо хвіст
          if (MAGIC_TAG.startsWith(possiblePartial) && possiblePartial !== _accumulatedText) {
            safeText = _accumulatedText.slice(0, _accumulatedText.length - possiblePartial.length)
          }
        }

        // 3. Рендеримо тільки "safe" частину (без хвоста-буфера)
        const idx = chatHistory.value.length - 1
        chatHistory.value = [
          ...chatHistory.value.slice(0, idx),
          { ...chatHistory.value[idx], content: safeText }
        ]

        // Micro-delay: kinetic typing cadence (0-20ms per word)
        const words = textChunk.trim().split(/\s+/)
        for (let i = 0; i < words.length; i++) {
          await _sleep(Math.random() * 20)
        }

        scrollToBottom()
      },
      (emotion) => {
        chefState.emotionDisplay = emotion
        chefStore.setEmotion(emotion)
      },
      (errMsg) => {
        error.value = "Chef error: " + errMsg
        chefState.emotionDisplay = 'ANGRY'
      }
    )
  } catch (err) {
    error.value = "Chef refused to chat: " + (err.message || 'Connection lost.')
    chefState.emotionDisplay = 'ANGRY'
  } finally {
    btnState.value = BUTTON_STATES.IDLE
    isStreaming.value = false

    // Фінальний flush: рендеримо ВЕСЬ _accumulatedText (тег вже strip-нутий)
    // Це гарантує що буферизований хвіст потрапить у фінальне повідомлення
    const lastIdx = chatHistory.value.length - 1
    const lastMsg = chatHistory.value[lastIdx]
    if (lastMsg?.role === 'assistant') {
      let finalText = lastMsg.content
      // Подвійна перевірка: _accumulatedText може містити залишки
      // якщо stream обірвався між chunks
      if (finalText.includes(MAGIC_TAG)) {
        finalText = finalText.replace(MAGIC_TAG, '')
        showMagicButton.value = true
      }
      // Беремо повний accumulated text (без тегу) як фінальний
      const fullClean = (_accumulatedText || '').replaceAll(MAGIC_TAG, '').trimEnd()
      if (fullClean && fullClean !== finalText) {
        chatHistory.value = [
          ...chatHistory.value.slice(0, lastIdx),
          { ...lastMsg, content: fullClean }
        ]
      }
    }
  }
}

const executeMagic = async (query = lastQuery.value) => {
  if (btnState.value === BUTTON_STATES.ACTIVE) return
  error.value = null
  btnState.value = BUTTON_STATES.ACTIVE
  showMagicButton.value = false
  chefState.showMagicTrigger = false

  try {
    if (query !== lastQuery.value) lastQuery.value = query

    // Bug 2 Fix: Спрощений flow — прямо до /generate-artifact без проміжного /advice
    // /advice часто повертає порожній summaries якщо запит нечіткий
    // Натомість: Chef вже сказав що потрібно — генеруємо RECIPE як default
    let artifactType = 'RECIPE'
    let artifactTitle = 'Chef\'s Recipe'

    // Спробуємо фазу 1 (/advice) як best-effort; якщо фейль — fallback на RECIPE
    try {
      const data = await getChefAdvice(query)
      const summaries = data?.chef_response?.technical_data?.artifact_summaries || []
      if (summaries.length > 0) {
        artifactType = summaries[0].artifact_type
        artifactTitle = summaries[0].title || artifactTitle
        console.debug('[Magic] Phase 1 OK — type:', artifactType, 'title:', artifactTitle)
      } else {
        console.warn('[Magic] Phase 1: no summaries, falling back to RECIPE')
      }
    } catch (adviceErr) {
      console.warn('[Magic] Phase 1 /advice failed, falling back to RECIPE:', adviceErr.message)
    }

    // Фаза 2: /generate-artifact — typed full artifact (ЗАВЖДИ виконується)
    console.debug('[Magic] Phase 2: generating', artifactType, 'for query:', query)
    const fullArtifact = await generateArtifact({
      title: artifactTitle,
      artifact_type: artifactType,
      context_parameters: query
    })

    console.debug('[Magic] Phase 2 result:', fullArtifact)

    if (!fullArtifact?.artifact || fullArtifact.artifact?.error) {
      throw new Error('Artifact data is empty or malformed: ' + JSON.stringify(fullArtifact?.artifact))
    }

    // Emit до App.vue → AdviceDisplay
    emit('artifact', {
      artifact_type: fullArtifact.artifact_type || artifactType,
      title: artifactTitle,
      data: fullArtifact.artifact
    })

    localInput.value = ''
  } catch (err) {
    console.error('[Magic] executeMagic failed:', err)
    error.value = 'Chef magic failed: ' + (err.message || 'Connection lost.')
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
