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

    // Get current widget DOM element width to prevent dragging entirely off-screen
    // The handle is inside the widget, so target is handle. Closest '.neo-widget-wrapper' is the container.
    const container = e.target.closest('.neo-widget-wrapper')
    const rect = container ? container.getBoundingClientRect() : { width: 350, height: 400 }

    const onMouseMove = (moveEvent) => {
      let newX = initialWidgetX + (moveEvent.clientX - startX)
      let newY = initialWidgetY + (moveEvent.clientY - startY)

      // Viewport constraints
      // Allow dragging but keep at least 100px visible horizontally and 40px vertically
      const minX = -(rect.width - 100)
      const maxX = window.innerWidth - 100
      const minY = 60 // Below top header
      const maxY = window.innerHeight - 100

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
