import { ref, reactive } from 'vue'

const BASE_URL = 'http://localhost:8000/api/v1'

export function useKitchenAPI() {
  const isLoading = ref(false)
  const error = ref(null)

  const fetchFridge = async () => {
    isLoading.value = true
    try {
      // Stubbing GET /fridge since we haven't explicitely added it yet in app.py
      // fallback to mock data until backend is fully wired
      const response = await fetch(`${BASE_URL}/fridge`).catch(() => null)
      if (response && response.ok) {
        const data = await response.json()
        return data.inventory || []
      }
      return [
        { name: 'Beef', days_left: 1, amount: 0.5, unit: 'kg', category: 'Meat' },
        { name: 'Milk', days_left: -1, amount: 1, unit: 'l', category: 'Dairy' },
        { name: 'Carrot', days_left: 5, amount: 3, unit: 'pcs', category: 'Veggies' },
      ]
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

  const scanReceipt = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resp = await fetch(`${BASE_URL}/scan-receipt`, {
        method: 'POST',
        body: formData
      })
      if (!resp.ok) throw new Error('Scan failed')
      return await resp.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return { isLoading, error, fetchFridge, getChefAdvice, scanReceipt }
}
