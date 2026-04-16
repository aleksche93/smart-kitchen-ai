import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useLayoutStore = defineStore('layout', () => {
  // Default grid setup if no DB record exists
  const widgets = ref([])
  const isLoaded = ref(false)
  let _debounceTimer = null

  // Fetch layout on load
  const fetchLayout = async () => {
    try {
      const resp = await fetch('http://localhost:8000/api/v1/ui/layout')
      if (resp.ok) {
        const data = await resp.json()
        const rawLayout = data.layout || []
        widgets.value = sanitizeLayout(rawLayout)
      }
    } catch (e) {
      console.warn('Failed to fetch UI layout', e)
    } finally {
      isLoaded.value = true
    }
  }

  // Push layout to backend
  const saveLayout = async () => {
    if (!isLoaded.value) return

    clearTimeout(_debounceTimer)
    _debounceTimer = setTimeout(async () => {
      try {
        await fetch('http://localhost:8000/api/v1/ui/layout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ layout: widgets.value })
        })
      } catch (e) {
        console.warn('Failed to persist UI layout', e)
      }
    }, 500) // 500ms debounce
  }

  // Force widgets save whenever deeply changed
  watch(widgets, () => {
    if (isLoaded.value) saveLayout()
  }, { deep: true })

  // Focus functionality (Z-Index elevation simulator)
  const focusWidget = (widgetId) => {
    // Basic array reorder could work, but we are using vuedraggable.
  }

  // Phase 10.2: Ghost Eradication & Strict State Registry
  const WIDGET_REGISTRY = ['fridge', 'chef_hub', 'advice']
  const sanitizeLayout = (layoutArray) => {
    if (!Array.isArray(layoutArray)) return []
    return layoutArray.filter(w => WIDGET_REGISTRY.includes(w.widget_id))
  }

  return { widgets, isLoaded, fetchLayout, focusWidget, saveLayout, sanitizeLayout }
})
