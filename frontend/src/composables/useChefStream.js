/**
 * useChefStream.js
 * ─────────────────
 * Unified SSE composable with Multi-Agent Demultiplexer.
 *
 * Stream Protocol:
 *   status  → {type: "status", data: {text: "...", intent?: "...", agent_id?: "chef"|"auditor"|"architect"}}
 *   delta   → {type: "delta",  data: {text: "...", intent: "...", agent_id?: "chef"|"auditor"|"architect"}}
 *   final   → {type: "final",  data: {payload: {...}}}
 */

import { ref, shallowRef } from 'vue'

const BASE_URL = 'http://localhost:8000/api/v1'

// Module-level singletons (shared across all composable instances)
const globalIsProcessing = ref(false)
const globalStreamingContent = ref('')   // RECIPE/ANALYTICS deltas → AdviceDisplay
const globalActiveProcessError = ref(null)
const globalDetectedIntent = ref(null)   // 'CHAT' | 'RECIPE' | 'ANALYTICS' | null

// Phase 15.2: Demultiplexer State
const globalActiveAgent = ref('chef') // 'chef', 'auditor', 'architect'
let globalActiveAgentTimeout = null

const globalAgentBuffers = {
  chef: shallowRef(''),
  auditor: shallowRef(''),
  architect: shallowRef('')
}

let globalAbortController = null

export function useChefStream() {
  const isProcessing = globalIsProcessing
  const streamingContent = globalStreamingContent
  const activeProcessError = globalActiveProcessError
  const detectedIntent = globalDetectedIntent
  const activeAgent = globalActiveAgent
  const agentBuffers = globalAgentBuffers

  const setActiveAgentSticky = (agentId) => {
    // If an Auditor/Architect is "sticky", ignore generic 'chef' events for a while
    if (agentId === 'chef' && globalActiveAgentTimeout) return

    activeAgent.value = agentId
    if (globalActiveAgentTimeout) {
      clearTimeout(globalActiveAgentTimeout)
      globalActiveAgentTimeout = null
    }
    
    // Only set reset timer if it's NOT chef
    if (agentId !== 'chef') {
      globalActiveAgentTimeout = setTimeout(() => {
        activeAgent.value = 'chef'
        globalActiveAgentTimeout = null
      }, 4000) // Increase to 4s for better visibility
    }
  }

  const clearAgentBuffers = () => {
    agentBuffers.chef.value = ''
    agentBuffers.auditor.value = ''
    agentBuffers.architect.value = ''
  }

  const appendAgentBuffer = (agent, textLine) => {
    if (!agentBuffers[agent]) return
    let current = agentBuffers[agent].value
    current += textLine + '\n'
    // Ring buffer: keep last 50 lines
    const lines = current.split('\n')
    if (lines.length > 50) {
      current = lines.slice(lines.length - 50).join('\n')
    }
    agentBuffers[agent].value = current
  }

  /**
   * startProcess
   * @param {Object}   payload          — Request body for /process
   * @param {Function} onStatus         — (text: string, data: Object) Called on status events
   * @param {Function} onFinal          — (data: Object) Called on the final event
   * @param {Function} onChatDelta      — (text: string) Called for CHAT delta chunks
   * @param {Function} onArtifactDelta  — (text: string) Called for RECIPE/ANALYTICS delta chunks
   */
  const startProcess = async (payload, onStatus, onFinal, onChatDelta, onArtifactDelta) => {
    isProcessing.value = true
    streamingContent.value = ''
    activeProcessError.value = null
    detectedIntent.value = null
    activeAgent.value = 'chef'
    
    // Phase 15.2 Hotfix: DO NOT reset buffers here to prevent amnesia per message.
    // Buffers now accumulate until clearAgentBuffers is called.

    globalAbortController = new AbortController()

    try {
      const response = await fetch(`${BASE_URL}/chef/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: globalAbortController.signal
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `API Error ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      const processEvent = (rawLine) => {
        const line = rawLine.trim()
        if (!line || !line.startsWith('data:')) return

        const jsonStr = line.replace(/^data:\s*/, '').trim()
        if (!jsonStr) return

        let event
        try {
          event = JSON.parse(jsonStr)
        } catch (e) {
          console.warn('[useChefStream] JSON parse error:', e.message)
          return
        }

        let agent = event.data?.agent_id || 'chef'
        const text = event.data?.text || ''

        // Phase 15.2 Hotfix: Detect agent from text markers if metadata is missing/generic
        if (text.includes('[The Fun Police]') || text.includes('Sin-Sieve') || text.includes('AUDIT')) {
          agent = 'auditor'
        } else if (text.includes('[The Mad Alchemist]')) {
          agent = 'architect'
        }

        if (event.type === 'status') {
          setActiveAgentSticky(agent)
          if (event.data?.intent) {
            detectedIntent.value = event.data.intent
          }
          
          if (text) {
             // Phase 15.2 Hotfix: Ticker should only show internal thoughts/status
             appendAgentBuffer(agent, `[STATUS] ${text}`)
          }

          if (onStatus) onStatus(text, event.data || {})

        } else if (event.type === 'delta') {
          // Visual switch with stickiness
          setActiveAgentSticky(agent)
          const intent = event.data?.intent || detectedIntent.value || 'RECIPE'

          // Removed agentBuffers append here to fix Stream Duplication
          
          if (intent === 'CHAT') {
            if (onChatDelta) onChatDelta(text)
          } else {
            streamingContent.value += text
            if (onArtifactDelta) onArtifactDelta(text)
          }

        } else if (event.type === 'final') {
          if (onFinal) onFinal(event.data)
        }
      }

      let done = false
      while (!done) {
        const result = await reader.read()
        done = result.done

        if (result.value) {
          buffer += decoder.decode(result.value, { stream: !done })
        }

        let separatorIdx
        while ((separatorIdx = buffer.indexOf('\n\n')) !== -1) {
          const completeMessage = buffer.slice(0, separatorIdx)
          buffer = buffer.slice(separatorIdx + 2)

          for (const line of completeMessage.split('\n')) {
            processEvent(line)
          }
        }
      }

      if (buffer.trim()) {
        for (const line of buffer.split('\n')) {
          processEvent(line)
        }
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('[useChefStream] Stream aborted by user.')
        activeProcessError.value = 'generation_stopped'
      } else {
        console.error('[useChefStream] Stream error:', err)
        activeProcessError.value = err.message
      }
    } finally {
      isProcessing.value = false
      globalAbortController = null
      
      // [CRITICAL FIX]: Не вбиваємо таймер миттєво, якщо стрім завершився дуже швидко!
      // Якщо таймер Аудитора/Архітектора ще йде — дозволяємо йому закінчитися природним шляхом.
      if (!globalActiveAgentTimeout) {
        activeAgent.value = 'chef'
      }
    }
  }

  const abortGeneration = () => {
    if (globalAbortController) {
      globalAbortController.abort()
    }
  }

  return {
    isProcessing,
    streamingContent,
    activeProcessError,
    detectedIntent,
    activeAgent,
    agentBuffers,
    startProcess,
    abortGeneration,
    clearAgentBuffers
  }
}
