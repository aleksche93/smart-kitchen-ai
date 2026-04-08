<template>
  <Teleport to="body">
    <!-- Draggable handle cursor preparation for Phase 10 -->
    <div class="fixed bottom-6 right-6 z-[100] w-full max-w-sm overflow-hidden bg-black/90 rounded-lg border border-slate-700/70 shadow-2xl font-mono text-xs transition-all duration-500"
         :class="isLoading ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'">
      
      <!-- Terminal Header -->
      <div class="bg-slate-800/80 px-3 py-1.5 flex items-center justify-between border-b border-slate-700/50 cursor-move">
        <div class="flex space-x-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
          <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
          <div class="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
        </div>
        <span class="text-[10px] text-slate-500 font-sans tracking-wide uppercase">AI Vision Agent</span>
        <div class="w-4"></div>
      </div>

      <!-- Terminal Body -->
      <div class="p-3 h-20 overflow-hidden relative flex flex-col justify-end">
        <transition-group name="slide-up" tag="div" class="flex flex-col space-y-1">
          <div v-for="(log, idx) in visibleLogs" :key="log.id" class="flex items-start text-green-400">
             <span class="opacity-70 mr-2">$</span>
             <span :class="{'opacity-50': idx !== visibleLogs.length - 1}">{{ log.text }}</span>
             <span v-if="idx === visibleLogs.length - 1" class="blink-cursor ml-1">_</span>
          </div>
        </transition-group>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'

const { isLoading } = useKitchenAPI()

const baseLogs = [
  "Analyzing OCR Stream...",
  "Checking for AI Agent Traps: [CLEAN]",
  "Checking Store Identity: Native Store Profile Detected",
  "Applying Native Language Rule...",
  "Sanitizing Data...",
  "Calculating Unit Prices..."
]

const visibleLogs = ref([])
let timer = null
let logIndex = 0

const startSimulation = () => {
  visibleLogs.value = []
  logIndex = 0
  
  const tick = () => {
    if (!isLoading.value) return
    
    visibleLogs.value.push({ id: Date.now(), text: baseLogs[logIndex] })
    if (visibleLogs.value.length > 3) visibleLogs.value.shift()
    
    logIndex++
    if (logIndex < baseLogs.length) {
      timer = setTimeout(tick, 1000 + Math.random() * 800)
    }
  }
  
  timer = setTimeout(tick, 500)
}

watch(isLoading, (newVal) => {
  if (newVal) {
    startSimulation()
  } else {
    clearTimeout(timer)
    setTimeout(() => {
      if (!isLoading.value) visibleLogs.value = []
    }, 500) // Delay clearing so it fades out
  }
})

onUnmounted(() => clearTimeout(timer))
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
</style>
