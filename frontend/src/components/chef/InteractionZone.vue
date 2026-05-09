<template>
  <div class="flex flex-col h-full bg-transparent overflow-hidden space-y-0 relative pb-2 pt-1 font-sans">
    
    <!-- Top Area: Actions Bar -->
    <div class="flex justify-between items-center bg-slate-800/80 px-4 py-2 flex-shrink-0 border border-slate-700/50 rounded-lg mb-3">
      <div class="flex items-center gap-4">
        <!-- Scan Receipt File Picker -->
        <label class="cursor-pointer text-xs uppercase tracking-wider font-bold text-slate-300 hover:text-keYellow transition-colors flex items-center group" title="Scan Receipt / Vision">
          <svg class="w-4 h-4 mr-1.5 opacity-70 group-hover:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          {{ $t('ui.actions.scan_receipt') }}
          <input type="file" accept="image/*" class="hidden" @change="handleFileUpload" />
        </label>
        <!-- Clear Session -->
        <button @click="handleClearSession" class="text-xs uppercase tracking-wider font-bold text-slate-400 hover:text-red-400 transition-colors flex items-center group">
          <svg class="w-4 h-4 mr-1.5 opacity-70 group-hover:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          {{ $t('ui.actions.clear_session') }}
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
              ? 'self-end bg-keBlue/20 text-keBlue px-4 py-2 rounded-2xl rounded-tr-sm max-w-[85%] break-words shadow-sm text-sm border border-keBlue/30'
              : 'self-start bg-slate-800/80 text-slate-300 px-4 py-3 rounded-2xl rounded-tl-sm max-w-[85%] shadow-md text-sm border border-slate-700/50 flex flex-col space-y-2'">
          <!-- Typing indicator: 3 dots — visible ONLY before first chunk arrives -->
          <span v-if="msg.role === 'assistant' && msg.content === '' && isStreaming" class="flex items-center gap-1 py-0.5">
            <span class="w-2 h-2 bg-keBlue rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-keBlue rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-keBlue rounded-full animate-bounce" style="animation-delay: 300ms"></span>
          </span>
          <!-- Content: renders as text arrives chunk by chunk (kinetic typing via SSE) -->
          <span v-else class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}<span
            v-if="msg.role === 'assistant' && isStreaming && index === chatHistory.length - 1 && msg.content !== ''"
            class="inline-block w-0.5 h-3.5 bg-keBlue ml-0.5 align-middle animate-pulse"
          ></span></span>
          <!-- Magic artifact trigger button — з'являється коли Шеф додає [ACTION: MAGIC_TRIGGER] -->
          <button v-if="msg.role === 'assistant' && index === chatHistory.length - 1 && showMagicButton" @click="executeMagic()" class="self-start mt-1 px-3 py-1.5 bg-keYellow/10 hover:bg-keYellow/20 text-keYellow border border-keYellow/30 rounded-full text-xs font-bold uppercase tracking-wider transition-all transform hover:scale-105 animate-fade-in-up flex items-center shadow-[0_0_10px_rgba(250,204,21,0.1)]">
             ✨ {{ $t('intents.magic_trigger_button') }}
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
            :placeholder="$t('ui.placeholders.ask_chef')"
            class="w-full bg-slate-900/50 border border-slate-600 focus:border-keBlue focus:ring-1 focus:ring-keBlue text-slate-200 rounded-full py-3 pl-5 pr-5 outline-none transition-all shadow-inner"
            @keyup.enter="handleAdvice"
          />
        </div>
        <button 
          @click="handleAdvice"
          :disabled="btnState === BUTTON_STATES.ACTIVE || !localInput.trim()"
          class="w-[100px] bg-keBlue hover:bg-blue-600 active:bg-blue-700 text-white font-medium rounded-full transition-all duration-300 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed shrink-0 shadow-md"
        >
          <span v-if="btnState === BUTTON_STATES.IDLE" class="text-sm">{{ $t('ui.actions.send') }}</span>
          <span v-else class="flex items-center text-xs whitespace-nowrap">
            <span class="mr-1 animate-pulse">{{ processingAction.icon }}</span>
            {{ processingAction.text }}
          </span>
        </button>
        <!-- Stop Button -->
        <button 
          v-if="isStreaming"
          @click="abortChat"
          class="w-12 h-12 bg-red-600/20 hover:bg-red-600/40 text-red-500 rounded-full flex items-center justify-center border border-red-500/30 transition-all active:scale-90"
          :title="$t('chef.actions.stop')"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" /></svg>
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
import { useChefStream } from '../../composables/useChefStream'

const { t } = useI18n()
const chefStore = useChefStore()
const { startProcess } = useChefStream()
const { isLoading, error, sendChatStream, scanReceipt, fetchFridge, fetchSessionHistory, clearSession, abortChat } = useKitchenAPI()
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
const AUDIT_TAG = '[ACTION: AUDIT_WARNING]'
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
      return { text: t('chef.processing.chopping'), icon: "🔪" }
   }
   if (lower.includes('water') || lower.includes('juice') || lower.includes('beer') || lower.includes('wine') || lower.includes('drink') || lower.includes('milk')) {
      return { text: t('chef.processing.pouring'), icon: "🫗" }
   }
   if (lower.includes('meat') || lower.includes('chicken') || lower.includes('beef') || lower.includes('pork')) {
      return { text: t('chef.processing.searing'), icon: "🥩" }
   }
   return { text: t('chef.processing.heating'), icon: "🍳" }
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
        const regexMagic = /\[ACTION: MAGIC_TRIGGER\]/g
        const regexAudit = /\[ACTION: AUDIT_WARNING\]/g
        
        if (regexMagic.test(_accumulatedText)) {
          _accumulatedText = _accumulatedText.replace(regexMagic, '')
          if (!showMagicButton.value) showMagicButton.value = true
        }
        
        if (regexAudit.test(_accumulatedText)) {
          _accumulatedText = _accumulatedText.replace(regexAudit, `⚠️ **${t('chef.audit.warning')}**: `)
        }

        // 2. Safe Render Buffer
        // Check if the current accumulated text ends with a partial tag
        let safeText = _accumulatedText
        const matchPartialMagic = _accumulatedText.match(/\[A?C?T?I?O?N?:?\s?M?A?G?I?C?_?T?R?I?G?G?E?R?]?$/)
        const matchPartialAudit = _accumulatedText.match(/\[A?C?T?I?O?N?:?\s?A?U?D?I?T?_?W?A?R?N?I?N?G?]?$/)
        
        if (matchPartialMagic && MAGIC_TAG.startsWith(matchPartialMagic[0])) {
          safeText = _accumulatedText.slice(0, _accumulatedText.length - matchPartialMagic[0].length)
        } else if (matchPartialAudit && AUDIT_TAG.startsWith(matchPartialAudit[0])) {
          safeText = _accumulatedText.slice(0, _accumulatedText.length - matchPartialAudit[0].length)
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
        error.value = t('errors.chef_error', { msg: errMsg })
        chefState.emotionDisplay = 'ANGRY'
      }
    )
  } catch (err) {
    error.value = t('errors.chef_refused', { msg: err.message || t('errors.connection_lost') })
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
      if (finalText.includes(AUDIT_TAG)) {
        finalText = finalText.replace(AUDIT_TAG, `⚠️ **${t('chef.audit.warning')}**: `)
      }
      // Беремо повний accumulated text (без тегу) як фінальний
      const fullClean = (_accumulatedText || '')
        .replaceAll(MAGIC_TAG, '')
        .replaceAll(AUDIT_TAG, `⚠️ **${t('chef.audit.warning')}**: `)
        .trimEnd()
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

    const payload = {
      title: "Chef's Artifact",
      artifact_type: "RECIPE",
      context_parameters: String(query || "")
    }
    console.debug('[Magic] Sending payload to /process:', payload)

    await startProcess(
      payload,
      (statusMsg) => {
        chefStore.logThought(statusMsg)
      },
      (finalData) => {
        // finalData is { payload: { artifact_type, content, metadata } }
        const actualPayload = finalData.payload || finalData
        const artifactData = actualPayload.metadata || actualPayload
        
        emit('artifact', {
          artifact_type: actualPayload.artifact_type || 'ORCHESTRATED_RESPONSE',
          title: artifactData.name || actualPayload.title || payload.title,
          data: artifactData
        })
      }
    )

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
