<template>
  <div class="flex flex-col h-full bg-transparent overflow-hidden space-y-0 relative pb-2 pt-1 font-sans">
    
    <!-- Top Area: Actions Bar -->
    <div class="flex justify-between items-center bg-slate-800/80 px-4 py-2 flex-shrink-0 border border-slate-700/50 rounded-lg mb-3">
      <div class="flex items-center gap-4">
        <!-- Scan Receipt File Picker -->
        <label class="cursor-pointer text-xs uppercase tracking-wider font-bold text-slate-300 hover:text-keYellow transition-colors flex items-center group" :title="$t('ui.actions.scan_receipt')">
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
         <!-- Thought Trace -->
         <details
           v-if="msg.role === 'assistant' && msg.thoughts?.length"
           :open="!msg.thoughtsCollapsed"
           class="thought-trace-details"
         >
           <summary class="list-none cursor-pointer select-none flex items-center gap-1
                          text-[10px] italic text-slate-500 hover:text-slate-400 transition-colors
                          [&::-webkit-details-marker]:hidden">
             <span class="opacity-60">&#9881;&#65039;</span>
             {{ $t('chef.thoughts_label') }} ({{ msg.thoughts.length }})
           </summary>
           <div class="flex flex-col gap-0.5 pt-1 pb-1">
             <span v-for="(th, ti) in msg.thoughts" :key="ti"
                   class="text-[10px] italic text-slate-500 leading-snug pl-3">
               {{ th }}
             </span>
           </div>
         </details>
         <!-- Typing indicator -->
         <span v-if="msg.role === 'assistant' && msg.content === '' && isStreaming" class="flex items-center gap-1 py-0.5">
           <span class="w-2 h-2 bg-keBlue rounded-full animate-bounce" style="animation-delay: 0ms"></span>
           <span class="w-2 h-2 bg-keBlue rounded-full animate-bounce" style="animation-delay: 150ms"></span>
           <span class="w-2 h-2 bg-keBlue rounded-full animate-bounce" style="animation-delay: 300ms"></span>
         </span>
         <!-- Content -->
         <span v-else class="whitespace-pre-wrap leading-relaxed" v-html="renderContent(msg, index)"></span>
         <!-- Magic artifact trigger button -->
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
            @keyup.enter="!isStreaming && handleAdvice()"
            :disabled="isStreaming"
          />
          <!-- Phase 13.5: Magic Trigger Button ✨ -->
          <button 
            v-if="!localInput && !isStreaming" 
            @click="executeMagic()"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-keYellow/60 hover:text-keYellow transition-all duration-300 p-1 hover:scale-125 hover:drop-shadow-[0_0_8px_rgba(250,204,21,0.4)]"
            :title="$t('intents.magic_trigger_button')"
          >
            ✨
          </button>
        </div>
        <!-- Morphing Send/Stop button -->
        <button
          @click="isStreaming ? handleAbort() : handleAdvice()"
          :disabled="!isStreaming && !localInput.trim()"
          :title="isStreaming ? $t('chef.actions.stop') : $t('ui.actions.send')"
          class="w-12 h-12 rounded-full flex items-center justify-center shrink-0 transition-all duration-200 active:scale-90 shadow-md disabled:opacity-40 disabled:cursor-not-allowed overflow-hidden"
          :class="isStreaming
            ? 'bg-red-600/30 hover:bg-red-600/50 border border-red-500/50 text-red-400'
            : 'bg-keBlue hover:bg-blue-600 text-white border border-transparent'"
        >
          <!-- Stop icon (square) -->
          <svg v-if="isStreaming" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14" rx="2" />
          </svg>
          <!-- Chef's Knife icon (🔪) — Replaces paper plane -->
          <svg v-else class="w-6 h-6 transform rotate-[45deg] group-hover:-translate-y-0.5 transition-all duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18 3L21 6L6 21H3V18L18 3Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 6L18 9" opacity="0.4" />
          </svg>
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

    <!-- Hidden canvas for receipt pre-processing -->
    <canvas ref="scanCanvas" class="hidden"></canvas>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onMounted, nextTick } from 'vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'
import { useChefFSM, chefState } from '../../composables/useChefFSM'
import ScannedReceiptOutput from './ScannedReceiptOutput.vue'
import HybridCropper from '../vision/HybridCropper.vue'
import { useI18n } from '../../plugins/i18n'
import { useChefStore } from '../../stores/chefStore'
import { useLayoutStore } from '../../stores/layoutStore'
import { useChefStream } from '../../composables/useChefStream'

const { t } = useI18n()
const chefStore = useChefStore()
const layoutStore = useLayoutStore()
const { startProcess, abortGeneration } = useChefStream()
const { error, scanReceipt, fetchFridge, fetchSessionHistory, clearSession } = useKitchenAPI()

const scanCanvas = ref(null)

const chatHistory = ref([])
const chatContainer = ref(null)
const isStreaming = ref(false)
let _scrollRAF = null
let _msgCounter = 0

const localInput = ref('')
const scannedItems = ref([])
const successMsg = ref(null)
const lastQuery = ref(null)
const rawImageObject = ref(null)

// --- Magic & Audit signal intercept tags ---
const MAGIC_TAG = '[ACTION: MAGIC_TRIGGER]'
const AUDIT_TAG = '[ACTION: AUDIT_WARNING]'
const showMagicButton = ref(false)
const emit = defineEmits(['artifact'])

const BUTTON_STATES = { IDLE: 'IDLE', ACTIVE: 'ACTIVE' }
const btnState = ref(BUTTON_STATES.IDLE)

// --- Scroll helper ---
const scrollToBottom = () => {
  if (_scrollRAF) cancelAnimationFrame(_scrollRAF)
  _scrollRAF = requestAnimationFrame(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// --- Restore session history on mount ---
const CHAT_STORAGE_KEY = 'chef_chat_history_v1'

const saveChatToStorage = () => {
  try {
    const serializable = chatHistory.value.map(m => ({ role: m.role, content: m.content }))
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(serializable))
  } catch (e) { /* storage unavailable */ }
}

onMounted(async () => {
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length) {
        chatHistory.value = parsed.map((m, i) => ({ ...m, _id: 'ls_' + i }))
        await nextTick()
        scrollToBottom()
        return
      }
    }
  } catch (e) { /* ignore */ }

  const historyData = await fetchSessionHistory()
  if (historyData?.messages?.length) {
    chatHistory.value = historyData.messages.map((m, i) => ({ ...m, _id: 'h_' + i }))
    saveChatToStorage()
    await nextTick()
    scrollToBottom()
  }
})

// --- Clear session ---
const handleClearSession = async () => {
  await clearSession()
  chatHistory.value = []
  lastQuery.value = null
  chefState.chatMessage = ''
  chefState.showMagicTrigger = false
  showMagicButton.value = false
  try { localStorage.removeItem(CHAT_STORAGE_KEY) } catch (e) { /* ignore */ }
}

// --- Abort stream ---
const handleAbort = () => {
  abortGeneration()
  isStreaming.value = false
  btnState.value = BUTTON_STATES.IDLE
}

const buildChatHistoryPayload = () => {
  return chatHistory.value
    .filter(m => m.content && m.content.trim())
    .map(m => ({ role: m.role, content: m.content.trim() }))
    .slice(-10)
}

const renderContent = (msg, index) => {
  if (msg.role === 'user') return msg.content
  let html = msg.content || ''
  
  const auditLabel = t('chef.audit.warning')
  const sieveRegex = new RegExp(`> ⚠️ \\*\\*${auditLabel}\\*\\*: (.*)`, 'g')
  
  html = html.replace(sieveRegex, (match, p1) => {
    return `
      <div class="sin-sieve-alert animate-fade-in">
        <div class="sin-icon">⚠️</div>
        <div class="sin-body">
          <div class="sin-header">${auditLabel}</div>
          <div class="sin-text">${p1}</div>
        </div>
      </div>
    `.trim()
  })

  if (isStreaming.value && index === chatHistory.value.length - 1 && msg.content !== '') {
    html += '<span class="inline-block w-0.5 h-3.5 bg-keBlue ml-0.5 align-middle animate-pulse"></span>'
  }

  return html
}

const handleAdvice = async () => {
  if (!localInput.value.trim() || btnState.value === BUTTON_STATES.ACTIVE) return
  error.value = null

  btnState.value = BUTTON_STATES.ACTIVE
  isStreaming.value = true

  const queryToSend = localInput.value.trim()
  lastQuery.value = queryToSend
  localInput.value = ''

  const userMsgId = 'msg_' + (++_msgCounter)
  const assistantMsgId = 'msg_' + (++_msgCounter)
  chatHistory.value = [
    ...chatHistory.value,
    { role: 'user', content: queryToSend, _id: userMsgId },
    { role: 'assistant', content: '', _id: assistantMsgId }
  ]
  scrollToBottom()

  let _accumulatedChatText = ''
  let _hasReceivedChatDelta = false
  let _thoughtsCollapsed = false
  const _bubbleThoughts = []

  const payload = {
    title: "Chef's Chat",
    artifact_type: "RECIPE",
    context_parameters: queryToSend,
    chat_history: buildChatHistoryPayload()
  }

  const _sleep = (ms) => new Promise(r => setTimeout(r, ms))

  const addThoughtToBubble = (text) => {
    if (_thoughtsCollapsed) return
    _bubbleThoughts.push(text)
    const idx = chatHistory.value.length - 1
    chatHistory.value = [
      ...chatHistory.value.slice(0, idx),
      { ...chatHistory.value[idx], thoughts: [..._bubbleThoughts] }
    ]
  }

  const onChatDelta = async (textChunk) => {
    _hasReceivedChatDelta = true
    if (!_thoughtsCollapsed) {
      _thoughtsCollapsed = true
      const idx = chatHistory.value.length - 1
      chatHistory.value = [
        ...chatHistory.value.slice(0, idx),
        { ...chatHistory.value[idx], thoughtsCollapsed: true }
      ]
    }

    _accumulatedChatText += textChunk
    const regexMagic = /\[ACTION: MAGIC_TRIGGER\]/g
    const regexAudit = /\[ACTION: AUDIT_WARNING\]/g

    if (regexMagic.test(_accumulatedChatText)) {
      _accumulatedChatText = _accumulatedChatText.replace(regexMagic, '')
      if (!showMagicButton.value) showMagicButton.value = true
    }
    if (regexAudit.test(_accumulatedChatText)) {
      _accumulatedChatText = _accumulatedChatText.replace(regexAudit, `⚠️ **${t('chef.audit.warning')}**: `)
    }

    let safeText = _accumulatedChatText
    const partialMagic = _accumulatedChatText.match(/\[A?C?T?I?O?N?:?\s?M?A?G?I?C?_?T?R?I?G?G?E?R?\]?$/)
    const partialAudit = _accumulatedChatText.match(/\[A?C?T?I?O?N?:?\s?A?U?D?I?T?_?W?A?R?N?I?N?G?\]?$/)
    if (partialMagic && MAGIC_TAG.startsWith(partialMagic[0])) {
      safeText = _accumulatedChatText.slice(0, -partialMagic[0].length)
    } else if (partialAudit && AUDIT_TAG.startsWith(partialAudit[0])) {
      safeText = _accumulatedChatText.slice(0, -partialAudit[0].length)
    }

    const msgIdx = chatHistory.value.findIndex(m => m._id === assistantMsgId)
    if (msgIdx !== -1) {
      chatHistory.value[msgIdx] = { ...chatHistory.value[msgIdx], content: safeText }
    }

    const words = textChunk.trim().split(/\s+/)
    for (let i = 0; i < words.length; i++) {
      await _sleep(Math.random() * 20)
    }
    scrollToBottom()
  }

  layoutStore.setChefStatus('COOKING')
  try {
    await startProcess(
      payload,
      (statusText, statusData) => {
        chefStore.logThought(statusText)
        if (statusData?.ui_thought) addThoughtToBubble(statusText)
      },
      (finalData) => {
        const actualPayload = finalData?.payload || finalData
        
        if (actualPayload?.artifact_type === 'CHAT') {
          const fullClean = _accumulatedChatText
            .replaceAll(MAGIC_TAG, '')
            .replaceAll(AUDIT_TAG, `> ⚠️ **${t('chef.audit.warning')}**: `)
            .trimEnd()
          
          const msgIdx = chatHistory.value.findIndex(m => m._id === assistantMsgId)
          if (msgIdx !== -1 && fullClean) {
            chatHistory.value[msgIdx] = { ...chatHistory.value[msgIdx], content: fullClean }
          }
          return
        }

        const artifactType = actualPayload?.artifact_type || 'ORCHESTRATED_RESPONSE'
        const confirmMsgText = t(`chef.responses.${artifactType.toLowerCase()}_ready`)
        
        const msgIdx = chatHistory.value.findIndex(m => m._id === assistantMsgId)
        if (msgIdx !== -1) {
          const existingContent = chatHistory.value[msgIdx].content || ''
          chatHistory.value[msgIdx] = {
            ...chatHistory.value[msgIdx],
            content: existingContent + (existingContent ? '\n\n' : '') + confirmMsgText,
            thoughtsCollapsed: true
          }
        }
        
        // Phase 13.5: Fix Empty Artifact - Pass metadata to upsertArtifact
        const artifactData = actualPayload?.metadata || actualPayload
        
        layoutStore.upsertArtifact({
          artifact_type: artifactType,
          title: artifactType === 'ANALYTICS' ? t('artifact.analytics.title') : (artifactData.name || 'Chef Advice'),
          data: artifactData
        })
        
        scrollToBottom()
      },
      onChatDelta,
      null
    )
  } catch (err) {
    if (err.name !== 'AbortError') {
      error.value = t('errors.chef_error', { msg: err.message || t('errors.connection_lost') })
      chefState.emotionDisplay = 'ANGRY'
    }
  } finally {
    btnState.value = BUTTON_STATES.IDLE
    isStreaming.value = false
    layoutStore.setChefStatus('IDLE')
    saveChatToStorage()
  }
}

const executeMagic = async (query = lastQuery.value) => {
  if (btnState.value === BUTTON_STATES.ACTIVE) return
  error.value = null
  btnState.value = BUTTON_STATES.ACTIVE
  showMagicButton.value = false
  chefState.showMagicTrigger = false

  layoutStore.setChefStatus('COOKING')
  try {
    if (query !== lastQuery.value) lastQuery.value = query

    const payload = {
      title: "Chef's Artifact",
      artifact_type: "RECIPE",
      context_parameters: String(query || ""),
      chat_history: buildChatHistoryPayload(),
      force_intent: "RECIPE"
    }

    await startProcess(
      payload,
      (statusMsg) => chefStore.logThought(statusMsg),
      (finalData) => {
        const actualPayload = finalData?.payload || finalData
        const artifactData = actualPayload?.metadata || actualPayload

        emit('artifact', {
          artifact_type: actualPayload?.artifact_type || 'ORCHESTRATED_RESPONSE',
          title: artifactData?.name || actualPayload?.title || payload.title,
          data: artifactData
        })
      },
      null,
      null
    )

    localInput.value = ''
  } catch (err) {
    if (err.name !== 'AbortError') {
      error.value = t('errors.chef_error', { msg: err.message || t('errors.connection_lost') })
      chefState.emotionDisplay = 'ANGRY'
    }
  } finally {
    btnState.value = BUTTON_STATES.IDLE
    layoutStore.setChefStatus('IDLE')
  }
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    error.value = t('errors.file_too_large')
    event.target.value = ''
    return
  }
  error.value = null
  rawImageObject.value = URL.createObjectURL(file)
  event.target.value = ''
}

const cancelCrop = () => {
  if (rawImageObject.value) {
    URL.revokeObjectURL(rawImageObject.value)
    rawImageObject.value = null
  }
}

const handleCroppedImage = async (blob) => {
  cancelCrop()
  error.value = null
  successMsg.value = null
  scannedItems.value = []

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
      chefState.chatMessage = data.items_added.some(item => item.is_bag) ? t('scan.bag_detected') : t('scan.no_bag')
    } else {
      scannedItems.value = data.items || Array.isArray(data) ? data : [data]
    }
    chefState.emotionDisplay = "FOCUSED"
  } catch (err) {
    error.value = err.message || t('errors.connection_lost')
    if (err.message?.toLowerCase().includes('duplicate')) fetchFridge()
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.sin-sieve-alert) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.75rem;
  background: rgba(127, 29, 29, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.75rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

:deep(.sin-icon) {
  font-size: 1.1rem;
  filter: drop-shadow(0 0 5px rgba(239, 68, 68, 0.5));
}

:deep(.sin-body) {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

:deep(.sin-header) {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  color: #f87171;
}

:deep(.sin-text) {
  font-size: 12px;
  color: #fca5a5;
  line-height: 1.4;
}
</style>
