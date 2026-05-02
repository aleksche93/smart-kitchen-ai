import { ref, reactive } from 'vue'

const BASE_URL = 'http://localhost:8000/api/v1'

// Shared global reactivity
const globalInventory = ref([])
const globalHistory = ref([])
const globalGhostReceipts = ref([])
const globalActiveTab = ref('kitchen')
const globalSelectedReceipt = ref(null)
const globalIsLoading = ref(false)
const globalError = ref(null)

export function useKitchenAPI() {
  const isLoading = globalIsLoading
  const error = globalError

  const fetchFridge = async () => {
    isLoading.value = true
    try {
      const response = await fetch(`${BASE_URL}/fridge`).catch(() => null)
      if (response && response.ok) {
        const data = await response.json()
        globalInventory.value = data.inventory || []
      }
      return globalInventory.value
    } catch (err) {
      error.value = err.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  const fetchHistory = async () => {
    isLoading.value = true
    try {
      const response = await fetch(`${BASE_URL}/fridge/history`).catch(() => null)
      if (response && response.ok) {
        const data = await response.json()
        globalHistory.value = data.history || []
      }
      return globalHistory.value
    } catch (err) {
      error.value = err.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  const getChefAdvice = async (ingredient) => {
    isLoading.value = true
    error.value = null
    try {
      const resp = await fetch(`${BASE_URL}/chef/advice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredient })
      })
      if (!resp.ok) {
        const errData = await resp.json()
        throw new Error(errData.detail || 'API Error')
      }
      return await resp.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchSessionHistory = async () => {
    try {
      const response = await fetch(`${BASE_URL}/chef/session/active/history`).catch(() => null)
      if (response && response.ok) {
        return await response.json()
      }
      return { messages: [] }
    } catch (err) {
      return { messages: [] }
    }
  }

  const clearSession = async () => {
    try {
      const resp = await fetch(`${BASE_URL}/chef/session/clear`, { method: 'POST' })
      if (resp.ok) return await resp.json()
    } catch (err) {
      console.error(err)
    }
  }

  const sendChatStream = async (message, onChunk, onMetadata, onError) => {
    isLoading.value = true
    error.value = null
    try {
      const resp = await fetch(`${BASE_URL}/chef/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      if (!resp.ok) {
         const errData = await resp.json().catch(() => ({}))
         throw new Error(errData.detail || `API Error ${resp.status}`)
      }
      
      const reader = resp.body.getReader()
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
               const dataStr = part.replace('data: ', '')
               try {
                  const data = JSON.parse(dataStr)
                  console.debug('[SSE]', data.type, data.type === 'chunk' ? data.text?.substring(0, 30) + '...' : data)
                  if (data.type === 'metadata') {
                     onMetadata && onMetadata(data.emotion)
                  } else if (data.type === 'chunk') {
                     onChunk && onChunk(data.text)
                  } else if (data.type === 'error') {
                     onError && onError(data.message)
                  } else if (data.type === 'done') {
                     console.debug('[SSE] Stream complete')
                  }
               } catch(e) { console.error("[SSE] Parse error:", dataStr, e) }
           }
        }
      }
    } catch (err) {
      error.value = err.message
      onError && onError(err.message)
    } finally {
      isLoading.value = false
    }
  }

  const deleteReceipt = async (receiptId) => {
    isLoading.value = true
    try {
      const receiptToDelete = globalHistory.value.find(r => r.id === receiptId)
      
      const resp = await fetch(`${BASE_URL}/fridge/receipt/${receiptId}`, {
        method: 'DELETE'
      })
      if (!resp.ok) throw new Error('Failed to delete receipt')
      
      // Store Ghost Metadata
      if (receiptToDelete) {
        globalGhostReceipts.value.push({
          id: receiptId,
          store_name: receiptToDelete.store_name,
          scan_date: receiptToDelete.scan_date
        })
      }
      
      // Reactivity: Refresh both synchronously
      await Promise.all([fetchFridge(), fetchHistory()])
      return true
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const scanReceipt = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resp = await fetch(`${BASE_URL}/fridge/receipt`, {
        method: 'POST',
        body: formData
      })
      if (!resp.ok) {
        if (resp.status === 409) throw new Error('Receipt already scanned (Duplicate)')
        const errData = await resp.json().catch(() => ({}))
        throw new Error(errData.detail || 'Scan failed')
      }
      const data = await resp.json()
      
      // Trigger global reactivity update synchronously
      await Promise.all([fetchFridge(), fetchHistory()])
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const generateArtifact = async ({ title, artifact_type, context_parameters = '' }) => {
    try {
      const resp = await fetch(`${BASE_URL}/chef/generate-artifact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, artifact_type, context_parameters })
      })
      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}))
        throw new Error(errData.detail || 'Artifact generation failed')
      }
      return await resp.json()  // { status, artifact_type, artifact: {...} }
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const cookRecipe = async (ingredients) => {
    try {
      const resp = await fetch(`${BASE_URL}/fridge/cook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients })
      })
      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}))
        throw new Error(errData.detail || 'Cook deduction failed')
      }
      const result = await resp.json()
      // Миттєве оновлення UI без page reload
      await fetchFridge()
      return result  // { status, deducted: [...], not_found: [...] }
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return { 
    isLoading, error, 
    inventory: globalInventory, history: globalHistory, ghostReceipts: globalGhostReceipts,
    activeTab: globalActiveTab, selectedReceipt: globalSelectedReceipt,
    fetchFridge, fetchHistory, getChefAdvice, sendChatStream, scanReceipt, deleteReceipt,
    fetchSessionHistory, clearSession, generateArtifact, cookRecipe
  }
}
