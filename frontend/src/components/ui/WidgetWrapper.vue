<template>
  <div v-show="!widget.isMinimized" class="neo-widget-wrapper bg-neoGray/30 backdrop-blur-md rounded-2xl border border-slate-700/50 shadow-2xl absolute flex flex-col transition-shadow duration-300"
       :style="{ left: widget.x + 'px', top: widget.y + 'px', width: widget.w + 'px', height: widget.is_collapsed ? '48px' : widget.h + 'px', zIndex: widget.z_index }"
       :class="{'ring-2 ring-neoBlue/50 shadow-neoBlue/20': isFocused}"
       @mousedown="handleFocus">
    
    <!-- Drag Handle and Header -->
    <div class="widget-header flex justify-between items-center px-4 py-2 border-b border-slate-700/50 bg-slate-800/50 rounded-t-2xl group">
      <div class="flex items-center space-x-3">
        <!-- Drag Handle Icon -->
        <span class="drag-handle text-slate-500 group-hover:text-neoBlue transition-colors select-none text-lg"
              @mousedown="startDrag">
          ⠿
        </span>
        <span class="text-xs font-bold tracking-widest text-slate-300 uppercase">
          {{ title }}
        </span>
      </div>
      
      <!-- Collapse toggle, Minimize and optional Close -->
      <div class="flex items-center space-x-2">
        <slot name="header-actions"></slot>
        <button @click.stop="toggleMinimize" class="text-slate-500 hover:text-neoYellow transition-colors p-1" title="Minimize to Dock">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" /></svg>
        </button>
        <button v-if="showClose" @click.stop="emit('close')" class="text-slate-500 hover:text-red-400 transition-colors p-1" title="Close Widget">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
        <button @click.stop="toggleCollapse" class="text-slate-500 hover:text-white transition-colors p-1" title="Toggle Collapse">
          <svg v-if="widget.is_collapsed" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" /></svg>
        </button>
      </div>
    </div>

    <!-- Widget Body Container (hidden if collapsed) -->
    <div v-show="!widget.is_collapsed" 
         class="widget-body flex-1 overflow-y-auto custom-scrollbar relative p-4 flex flex-col">
      <slot />
    </div>

    <!-- Resize Handles -->
    <div v-show="!widget.is_collapsed" class="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize z-50" @mousedown.stop.prevent="startResize($event, 'se')"></div>
    <div v-show="!widget.is_collapsed" class="absolute bottom-0 left-0 w-4 h-4 cursor-sw-resize z-50" @mousedown.stop.prevent="startResize($event, 'sw')"></div>
    <div v-show="!widget.is_collapsed" class="absolute top-0 right-0 w-4 h-4 cursor-ne-resize z-50" @mousedown.stop.prevent="startResize($event, 'ne')"></div>
    <div v-show="!widget.is_collapsed" class="absolute top-0 left-0 w-4 h-4 cursor-nw-resize z-50" @mousedown.stop.prevent="startResize($event, 'nw')"></div>

  </div>
</template>

<script setup>
import { useDraggable } from '../../composables/useDraggable'
import { useLayoutStore } from '../../stores/layoutStore'

const layoutStore = useLayoutStore()
const { initDrag } = useDraggable()

const props = defineProps({
  widget: {
    type: Object,
    required: true
  },
  title: {
    type: String,
    default: 'Widget'
  },
  isFocused: {
    type: Boolean,
    default: false
  },
  isDragged: {
    type: Boolean,
    default: false
  },
  showClose: {
    type: Boolean,
    default: false
  },
  minHeight: {
    type: Number,
    default: 0
  },
  maxHeight: {
    type: Number,
    default: 500
  }
})

const emit = defineEmits(['focus', 'update:collapse', 'close'])

const handleFocus = () => {
  layoutStore.bringToFront(props.widget.widget_id)
  emit('focus')
}

const startDrag = (e) => {
  initDrag(e, props.widget.widget_id, layoutStore)
}

const toggleMinimize = () => {
  props.widget.isMinimized = true
  layoutStore.saveLayout()
}

const toggleCollapse = () => {
  emit('update:collapse', !props.widget.is_collapsed)
}

// Resizing logic
const startResize = (e, corner) => {
  if (e.button !== 0) return
  handleFocus()
  
  const startX = e.clientX
  const startY = e.clientY
  const startW = props.widget.w || 300
  const startH = props.widget.h || 400
  const startObjX = props.widget.x || 0
  const startObjY = props.widget.y || 0
  
  const minWidth = 300
  const minHeight = 200

  const onMouseMove = (moveEvent) => {
    const dx = moveEvent.clientX - startX
    const dy = moveEvent.clientY - startY
    
    let newW = startW
    let newH = startH
    let newX = startObjX
    let newY = startObjY
    
    if (corner.includes('e')) newW = Math.max(minWidth, startW + dx)
    if (corner.includes('s')) newH = Math.max(minHeight, startH + dy)
    
    if (corner.includes('w')) {
      newW = Math.max(minWidth, startW - dx)
      if (newW > minWidth) newX = startObjX + dx
    }
    if (corner.includes('n')) {
      newH = Math.max(minHeight, startH - dy)
      if (newH > minHeight) newY = startObjY + dy
    }
    
    props.widget.w = newW
    props.widget.h = newH
    props.widget.x = newX
    props.widget.y = newY
  }
  
  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    layoutStore.saveLayout()
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}
</script>

<style scoped>
.drag-handle {
  cursor: grab;
}
.drag-handle:active {
  cursor: grabbing;
}
</style>
