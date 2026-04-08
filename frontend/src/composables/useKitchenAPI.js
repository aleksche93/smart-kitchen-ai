import { ref, reactive } from 'vue'

const BASE_URL = 'http://localhost:8000/api/v1'

// Shared global reactivity
const globalInventory = ref([])
const globalHistory = ref([])
const globalActiveTab = ref('kitchen')
const globalSelectedReceipt = ref(null)

export function useKitchenAPI() {
  const isLoading = ref(false)
  const error = ref(null)

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

  const deleteReceipt = async (receiptId) => {
    isLoading.value = true
    try {
      const resp = await fetch(`${BASE_URL}/fridge/receipt/${receiptId}`, {
        method: 'DELETE'
      })
      if (!resp.ok) throw new Error('Failed to delete receipt')
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

  return { 
    isLoading, error, 
    inventory: globalInventory, history: globalHistory, 
    activeTab: globalActiveTab, selectedReceipt: globalSelectedReceipt,
    fetchFridge, fetchHistory, getChefAdvice, scanReceipt, deleteReceipt 
  }
}
