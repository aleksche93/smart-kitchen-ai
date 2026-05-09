/**
 * useChefStream.js
 * ─────────────────
 * Single SSE composable for the unified /api/v1/chef/process endpoint.
 *
 * Stream Protocol:
 *   status  → {type: "status", data: {text: "...", intent?: "CHAT"|"RECIPE"|"ANALYTICS", ui_thought?: true}}
 *   delta   → {type: "delta",  data: {text: "...", intent: "CHAT"|"RECIPE"|"ANALYTICS"}}
 *   final   → {type: "final",  data: {payload: {...}}}
 *
 * Buffer Strategy (Prompter-approved):
 *   TextDecoder chunks may split a message mid-JSON. We use a string accumulator:
 *   1. Append each decoded chunk to `buffer`.
 *   2. While buffer contains '\n\n' — extract and process the complete message.
 *   3. Keep the remaining partial message in `buffer` for the next chunk.
 *   This is the ONLY correct way to handle streaming SSE over fetch.
 */

import { ref } from 'vue'

const BASE_URL = 'http://localhost:8000/api/v1'

// Module-level singletons (shared across all composable instances)
const globalIsProcessing = ref(false)
const globalStreamingContent = ref('')   // RECIPE/ANALYTICS deltas → AdviceDisplay
const globalActiveProcessError = ref(null)
const globalDetectedIntent = ref(null)   // 'CHAT' | 'RECIPE' | 'ANALYTICS' | null
let globalAbortController = null

export function useChefStream() {
  const isProcessing = globalIsProcessing
  const streamingContent = globalStreamingContent
  const activeProcessError = globalActiveProcessError
  const detectedIntent = globalDetectedIntent

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

      // ─── Accumulator buffer — the correct SSE approach ────────────────────
      // Each TextDecoder chunk may contain partial messages or multiple messages.
      // We accumulate everything and only process COMPLETE messages (delimited by \n\n).
      let buffer = ''

      const processEvent = (rawLine) => {
        // rawLine is a single SSE line like: "data: {...}"
        const line = rawLine.trim()
        if (!line || !line.startsWith('data:')) return  // heartbeat or empty

        const jsonStr = line.replace(/^data:\s*/, '').trim()
        if (!jsonStr) return

        let event
        try {
          event = JSON.parse(jsonStr)
        } catch (e) {
          console.warn('[useChefStream] JSON parse error on line:', jsonStr.slice(0, 80), e.message)
          return  // Skip malformed event — do NOT crash the stream
        }

        if (event.type === 'status') {
          // Capture intent as soon as the orchestrator broadcasts it
          if (event.data?.intent) {
            detectedIntent.value = event.data.intent
          }
          // Pass full data object as 2nd arg so callers can inspect ui_thought flag
          if (onStatus) onStatus(event.data?.text || '', event.data || {})

        } else if (event.type === 'delta') {
          const text = event.data?.text || ''
          const intent = event.data?.intent || detectedIntent.value || 'RECIPE'

          if (intent === 'CHAT') {
            // Route to chat bubble (kinetic typing effect)
            if (onChatDelta) onChatDelta(text)
          } else {
            // RECIPE and ANALYTICS both route to AdviceDisplay streaming view
            streamingContent.value += text
            if (onArtifactDelta) onArtifactDelta(text)
          }

        } else if (event.type === 'final') {
          if (onFinal) onFinal(event.data)
        }
      }

      // ─── Read loop ────────────────────────────────────────────────────────
      let done = false
      while (!done) {
        const result = await reader.read()
        done = result.done

        if (result.value) {
          buffer += decoder.decode(result.value, { stream: !done })
        }

        // Process ALL complete messages in the buffer
        // A complete SSE message ends with \n\n (two consecutive newlines)
        let separatorIdx
        while ((separatorIdx = buffer.indexOf('\n\n')) !== -1) {
          const completeMessage = buffer.slice(0, separatorIdx)
          buffer = buffer.slice(separatorIdx + 2)  // Move past the \n\n

          // A message block may contain multiple "data:" lines (though rare with our backend)
          // Process each line separately
          for (const line of completeMessage.split('\n')) {
            processEvent(line)
          }
        }
      }

      // Flush any remaining buffer content (edge case: stream ended without trailing \n\n)
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
      // ALWAYS reset isProcessing — even on error or abort
      isProcessing.value = false
      globalAbortController = null
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
    startProcess,
    abortGeneration
  }
}
