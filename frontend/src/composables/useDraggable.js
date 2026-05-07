import { onUnmounted } from 'vue'

export function useDraggable() {
  const initDrag = (e, widgetId, layoutStore) => {
    // Only left click
    if (e.button !== 0) return

    const widget = layoutStore.widgets.find(w => w.widget_id === widgetId)
    if (!widget) return

    layoutStore.bringToFront(widgetId)

    const startX = e.clientX
    const startY = e.clientY
    const initialWidgetX = widget.x || 0
    const initialWidgetY = widget.y || 0
    
    const widgetWidth = widget.w || 350
    const widgetHeight = widget.is_collapsed ? 48 : (widget.h || 400)

    const onMouseMove = (moveEvent) => {
      // Calculate scale if CSS zoom/scale is applied to body
      const scale = parseFloat(getComputedStyle(document.body).getPropertyValue('--zoom-scale')) || 1;
      
      const deltaX = (moveEvent.clientX - startX) / scale;
      const deltaY = (moveEvent.clientY - startY) / scale;

      let newX = initialWidgetX + deltaX
      let newY = initialWidgetY + deltaY

      // Viewport constraints (Adaptive Canvas)
      const canvasWidth = Math.max(window.innerWidth, 1440)
      const canvasHeight = Math.max(window.innerHeight, 800)
      
      const minX = 0
      const maxX = Math.max(0, canvasWidth - widgetWidth)
      const minY = 60 // Below top header
      const maxY = Math.max(minY, canvasHeight - widgetHeight)

      newX = Math.max(minX, Math.min(newX, maxX))
      newY = Math.max(minY, Math.min(newY, maxY))

      widget.x = newX
      widget.y = newY
    }

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
      layoutStore.saveLayout()
    }

    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
  }

  return { initDrag }
}
