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

  // Phase 12.2: Spatial OS Grid Destruction
  const WIDGET_REGISTRY = ['fridge', 'chef_hub', 'advice']
  
  // Default coordinates for a 1920x1080 screen roughly
  const defaultCoords = {
    'fridge': { x: 20, y: 80, w: 400, h: 600 },
    'chef_hub': { x: 440, y: 80, w: 400, h: 700 },
    'advice': { x: 860, y: 80, w: 500, h: 800 }
  }

  const sanitizeLayout = (layoutArray) => {
    if (!Array.isArray(layoutArray)) layoutArray = []
    
    // Ensure all required widgets exist
    const currentIds = layoutArray.map(w => w.widget_id)
    const missing = WIDGET_REGISTRY.filter(id => !currentIds.includes(id))
    
    const augmented = [...layoutArray, ...missing.map(id => ({ widget_id: id }))]

    return augmented
      .filter(w => WIDGET_REGISTRY.includes(w.widget_id))
      .map(w => {
        const def = defaultCoords[w.widget_id] || { x: 100, y: 100, w: 300, h: 400 }
        return {
          ...w,
          x: typeof w.x === 'number' ? w.x : def.x,
          y: typeof w.y === 'number' ? w.y : def.y,
          w: typeof w.w === 'number' ? w.w : def.w,
          h: typeof w.h === 'number' ? w.h : def.h,
          isMinimized: w.isMinimized || false,
          is_collapsed: w.is_collapsed || false,
          z_index: w.z_index ?? 10,
          rotation_angle: w.rotation_angle ?? 0.0
        }
      })
  }

  // Focus functionality (Z-Index elevation simulator)
  const focusWidget = (widgetId) => bringToFront(widgetId)
  
  const bringToFront = (widgetId) => {
    const maxZ = Math.max(0, ...widgets.value.map(w => w.z_index || 0))
    const widget = widgets.value.find(w => w.widget_id === widgetId)
    if (widget && widget.z_index < maxZ) {
      widget.z_index = maxZ + 1
      saveLayout()
    }
  }

  // Phase 12.1 Step C: Dynamic Resize & Focus Mode
  const isAdviceMaximized = ref(false)
  const focusedArtifact = ref(null)  // { artifact_type, title, data }

  const toggleAdviceMaximized = () => {
    isAdviceMaximized.value = !isAdviceMaximized.value
  }

  const setFocusedArtifact = (artifact) => {
    focusedArtifact.value = artifact
  }

  const clearFocusedArtifact = () => {
    focusedArtifact.value = null
  }

  return {
    widgets, isLoaded, fetchLayout, focusWidget, saveLayout, sanitizeLayout,
    isAdviceMaximized, focusedArtifact,
    toggleAdviceMaximized, setFocusedArtifact, clearFocusedArtifact, bringToFront
  }
})
