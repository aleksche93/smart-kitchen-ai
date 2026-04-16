<template>
  <div class="neo-widget-wrapper bg-neoGray/30 backdrop-blur-md rounded-2xl border border-slate-700/50 shadow-2xl relative flex flex-col transition-shadow duration-300"
       :class="{'ring-2 ring-neoBlue/50 shadow-neoBlue/20': isFocused, 'z-50': isDragged, 'z-10': !isDragged, 'h-12': widget.is_collapsed, 'h-auto': !widget.is_collapsed}"
       @mousedown="emit('focus')">
    
    <!-- Drag Handle and Header -->
    <div class="widget-header flex justify-between items-center px-4 py-2 border-b border-slate-700/50 bg-slate-800/50 rounded-t-2xl group">
      <div class="flex items-center space-x-3">
        <!-- Drag Handle Icon (sortablejs relies on handle class) -->
        <span class="drag-handle text-slate-500 group-hover:text-neoBlue transition-colors select-none text-lg">
          ⠿
        </span>
        <span class="text-xs font-bold tracking-widest text-slate-300 uppercase">
          {{ title }}
        </span>
      </div>
      
      <!-- Collapse toggle and optional Close -->
      <div class="flex items-center space-x-2">
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
         class="widget-body flex-1 overflow-y-auto custom-scrollbar relative p-4 flex flex-col"
         :style="{ maxHeight: maxHeight + 'px', minHeight: (!widget.is_collapsed && minHeight) ? minHeight + 'px' : undefined }">
      <slot />
    </div>

  </div>
</template>

<script setup>

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

const toggleCollapse = () => {
  emit('update:collapse', !props.widget.is_collapsed)
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
