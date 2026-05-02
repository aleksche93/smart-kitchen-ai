<template>
  <div class="artifact-card group relative transition-all duration-500 ease-out"
       :class="[isFocused ? 'scale-105 z-50' : 'hover:scale-[1.02]', typeColorClass]"
       :style="spatialStyle"
       @click="$emit('focus')">
    
    <!-- Glow Ring -->
    <div class="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
         :class="glowClass"></div>

    <!-- Card Body -->
    <div class="relative bg-slate-900/90 backdrop-blur-xl rounded-2xl border overflow-hidden transition-all duration-300"
         :class="isFocused ? 'border-' + accentColor + '/60 shadow-2xl' : 'border-slate-700/50 shadow-lg'">
      
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3 border-b border-slate-700/40">
        <div class="flex items-center gap-2">
          <span class="text-lg">{{ typeIcon }}</span>
          <div>
            <h3 class="text-sm font-bold text-slate-200 truncate">{{ artifact.title || 'Artifact' }}</h3>
            <span class="text-[10px] uppercase tracking-widest font-bold" :class="'text-' + accentColor + '/80'">{{ artifact.artifact_type }}</span>
          </div>
        </div>
        <button v-if="isFocused" @click.stop="$emit('close')"
                class="text-slate-500 hover:text-slate-300 transition-colors p-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Dynamic Content Slot -->
      <div class="p-4 max-h-[400px] overflow-y-auto custom-scrollbar">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  artifact: { type: Object, required: true },
  rotationAngle: { type: Number, default: 0 },
  zIndex: { type: Number, default: 1 },
  isFocused: { type: Boolean, default: false }
})

defineEmits(['focus', 'close'])

const typeConfig = computed(() => {
  const configs = {
    RECIPE: { icon: '🍽️', color: 'neoYellow', glow: 'shadow-[0_0_30px_rgba(250,204,21,0.15)]' },
    SHOPPING_LIST: { icon: '🛒', color: 'emerald-400', glow: 'shadow-[0_0_30px_rgba(52,211,153,0.15)]' },
    WASTE_ALERT: { icon: '⚠️', color: 'red-400', glow: 'shadow-[0_0_30px_rgba(248,113,113,0.15)]' },
    PREP_SCHEDULE: { icon: '📋', color: 'blue-400', glow: 'shadow-[0_0_30px_rgba(96,165,250,0.15)]' },
    TASK_LIST: { icon: '✅', color: 'purple-400', glow: 'shadow-[0_0_30px_rgba(192,132,252,0.15)]' }
  }
  return configs[props.artifact.artifact_type] || configs.RECIPE
})

const typeIcon = computed(() => typeConfig.value.icon)
const accentColor = computed(() => typeConfig.value.color)
const typeColorClass = computed(() => '')
const glowClass = computed(() => typeConfig.value.glow)

const spatialStyle = computed(() => ({
  transform: `perspective(800px) rotateY(${props.isFocused ? 0 : props.rotationAngle}deg)`,
  zIndex: props.isFocused ? 100 : props.zIndex,
  transition: 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), z-index 0.3s'
}))
</script>
