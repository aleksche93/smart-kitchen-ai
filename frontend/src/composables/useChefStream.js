import { ref } from 'vue'

const BASE_URL = 'http://localhost:8000/api/v1'

const globalIsProcessing = ref(false)
const globalStreamingContent = ref('')
const globalActiveProcessError = ref(null)
let globalAbortController = null

export function useChefStream() {
  const isProcessing = globalIsProcessing
  const streamingContent = globalStreamingContent
  const activeProcessError = globalActiveProcessError

  
  let abortController = null

  const startProcess = async (payload, onStatus, onFinal) => {
    isProcessing.value = true
    streamingContent.value = ''
    activeProcessError.value = null
    
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

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        
        const parts = buffer.split('\n\n')
        buffer = parts.pop()

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const dataStr = part.replace(/^data:\s*/, '').trim()
            if (!dataStr) continue
            
            try {
              const data = JSON.parse(dataStr)
              
              if (data.type === 'status') {
                if (onStatus) onStatus(data.data.text)
              } else if (data.type === 'delta') {
                streamingContent.value += data.data.text
              } else if (data.type === 'final') {
                if (onFinal) onFinal(data.data)
                break
              }
            } catch (e) {
              console.warn('[SSE] Parse error, restoring buffer', e, dataStr)
              // If parsing fails despite \n\n (e.g. malformed JSON), put it back to buffer to try next time
              buffer = part + '\n\n' + buffer
              break
            }
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('[useChefStream] Stream aborted by user')
        activeProcessError.value = 'Generation stopped.'
      } else {
        activeProcessError.value = err.message
      }
    } finally {
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
    startProcess,
    abortGeneration
  }
}
