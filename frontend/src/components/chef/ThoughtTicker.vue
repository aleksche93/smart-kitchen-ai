<template>
  <Teleport to="body">
    <Transition name="ticker-float">
      <div v-show="isVisible"
           ref="tickerEl"
           class="fixed z-[1000] select-none font-mono text-xs"
           :style="{ left: pos.x + 'px', top: pos.y + 'px', width: isMinimized ? '48px' : '320px' }"
      >
        <!-- Minimized State -->
        <div v-if="isMinimized"
             @click="isMinimized = false"
             class="w-12 h-12 rounded-full bg-slate-900/80 backdrop-blur-xl border border-green-500/30 flex items-center justify-center cursor-pointer hover:border-green-400/60 hover:scale-110 transition-all shadow-[0_0_15px_rgba(34,197,94,0.2)] group">
          <span class="text-green-400 text-lg group-hover:animate-pulse">$</span>
        </div>

        <!-- Full Ticker -->
        <div v-else
             class="bg-slate-900/85 backdrop-blur-xl rounded-xl border border-slate-700/50 shadow-2xl overflow-hidden transition-all duration-300 hover:opacity-100"
             :class="isDragging ? 'opacity-100 ring-2 ring-green-500/30' : 'opacity-75'">
          
          <!-- Header (Drag Handle) -->
          <div class="flex items-center justify-between px-3 py-1.5 border-b border-slate-700/40 cursor-grab active:cursor-grabbing bg-slate-800/60"
               @mousedown="startDrag">
            <div class="flex items-center gap-2">
              <span class="text-green-400 animate-pulse text-[10px]">●</span>
              <span class="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Chef HUD</span>
            </div>
            <div class="flex items-center gap-1">
              <button @click.stop="isMinimized = true"
                      class="text-slate-500 hover:text-slate-300 transition-colors p-0.5" title="Minimize">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6" /></svg>
              </button>
            </div>
          </div>

          <!-- Terminal Body -->
          <div class="p-3 max-h-[160px] overflow-y-auto flex flex-col justify-end custom-scrollbar">
            <transition-group name="slide-up" tag="div" class="flex flex-col space-y-1">
              <div v-for="(log, idx) in thoughts" :key="log.id" class="flex items-start">
                <span class="opacity-70 mr-2 text-green-600">$</span>
                <span v-if="idx !== thoughts.length - 1" class="opacity-50 text-green-400/70">{{ log.text }}</span>
                <span v-else class="text-green-400">{{ displayText }}</span>
                <span v-if="idx === thoughts.length - 1" class="blink-cursor ml-1 text-green-400">_</span>
              </div>
            </transition-group>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onUnmounted, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useKitchenAPI } from '../../composables/useKitchenAPI'
import { useChefStore } from '../../stores/chefStore'
import { useTypewriter } from '../../composables/useTypewriter'

const { isLoading } = useKitchenAPI()
const chefStore = useChefStore()
const { thoughts } = storeToRefs(chefStore)

const { displayText, type, abort } = useTypewriter()

const isVisible = ref(false)
const isMinimized = ref(false)
const isDragging = ref(false)
const tickerEl = ref(null)
let hideTimer = null

// Position (bottom-right default)
const pos = ref({ x: window.innerWidth - 340, y: window.innerHeight - 230 })

// Drag logic
let dragOffset = { x: 0, y: 0 }

const startDrag = (e) => {
  isDragging.value = true
  dragOffset.x = e.clientX - pos.value.x
  dragOffset.y = e.clientY - pos.value.y
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (e) => {
  pos.value = {
    x: Math.max(0, Math.min(window.innerWidth - 340, e.clientX - dragOffset.x)),
    y: Math.max(0, Math.min(window.innerHeight - 60, e.clientY - dragOffset.y))
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// Visibility logic
watch(isLoading, (newVal) => {
  if (newVal) {    
    isVisible.value = true
    if (hideTimer) clearTimeout(hideTimer)
  } else {
    hideTimer = setTimeout(() => {
      isVisible.value = false
    }, 5000)
  }
})

watch(() => thoughts.value.length, async () => {
  isVisible.value = true
  if (hideTimer) clearTimeout(hideTimer)
  
  if (thoughts.value.length > 0) {
    const latestThought = thoughts.value[thoughts.value.length - 1]
    abort()
    await type(latestThought.text)
  }

  hideTimer = setTimeout(() => {
    if (!isLoading.value) isVisible.value = false
  }, 5000)
})

onMounted(() => {
  chefStore.startSarcasticEngine()
  // Recalculate position on resize
  window.addEventListener('resize', () => {
    pos.value = {
      x: Math.min(pos.value.x, window.innerWidth - 340),
      y: Math.min(pos.value.y, window.innerHeight - 60)
    }
  })
})

onUnmounted(() => {
  clearTimeout(hideTimer)
  chefStore.stopSarcasticEngine()
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.blink-cursor {
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.ticker-float-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.ticker-float-leave-active {
  transition: all 0.3s ease-in;
}
.ticker-float-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}
.ticker-float-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(10px);
  filter: blur(4px);
}
</style>
