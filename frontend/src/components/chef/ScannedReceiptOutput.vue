<template>
  <Teleport to="body">
    <div v-if="items && items.length > 0" class="fixed bottom-6 right-6 w-[400px] z-50 animate-fade-in-up transition-all duration-300 origin-bottom-right" :class="{ 'is-burning': isBurning }">
      <div class="bg-slate-800/90 backdrop-blur-md border border-keBlue/30 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(56,189,248,0.15)] flex flex-col max-h-[60vh] relative">
        <div class="bg-keBlue/20 border-b border-keBlue/30 px-4 py-3 flex justify-between items-center shrink-0">
          <h3 class="text-sm font-bold text-keBlue uppercase tracking-wider flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Parsed Receipt Data
          </h3>
          <button @click="manualClose" class="text-slate-400 hover:text-white transition-colors bg-slate-700/50 hover:bg-slate-600 rounded-full p-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="overflow-y-auto custom-scrollbar flex-1 p-2 mb-1">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-700/50 text-slate-400 sticky top-0 backdrop-blur-md z-10 rounded-lg">
              <tr>
                <th class="px-3 py-2 font-medium rounded-tl-lg">Product</th>
                <th class="px-3 py-2 font-medium">Cat</th>
                <th class="px-3 py-2 font-medium rounded-tr-lg">Qty</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/50">
              <tr v-for="(item, idx) in items" :key="idx" class="hover:bg-slate-700/30 transition-colors">
                <td class="px-3 py-2 font-semibold text-slate-200 capitalize truncate max-w-[150px]">{{ item.name }}</td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 rounded-md bg-slate-700/80 text-[10px] uppercase font-bold tracking-wider text-slate-300 border border-slate-600">
                    {{ item.category || 'Other' }}
                  </span>
                </td>
                <td class="px-3 py-2 flex items-center space-x-1">
                  <span class="text-keYellow font-mono">{{ item.quantity || item.amount || 1 }}</span>
                  <span class="text-slate-500 text-[10px] uppercase">{{ item.unit || 'pcs' }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Progress Bar -->
        <div class="absolute bottom-0 left-0 h-1 bg-slate-700 w-full">
          <div class="h-full bg-keYellow transition-all duration-100 ease-linear" :style="{ width: progressPercentage + '%' }" :class="{'bg-red-500': timeLeft <= 2}"></div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['clear'])

const TIMER_DURATION = 10 // seconds
const timeLeft = ref(TIMER_DURATION)
const isBurning = ref(false)
let intervalId = null

const progressPercentage = computed(() => {
  return (timeLeft.value / TIMER_DURATION) * 100
})

const startTimer = () => {
  stopTimer()
  timeLeft.value = TIMER_DURATION
  isBurning.value = false
  intervalId = setInterval(() => {
    timeLeft.value -= 0.1 // update every 100ms
    if (timeLeft.value <= 4.0 && !isBurning.value) {
      isBurning.value = true // trigger burn animation at 4 seconds
    }
    if (timeLeft.value <= 0) {
      stopTimer()
      emit('clear')
    }
  }, 100)
}

const stopTimer = () => {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}

const manualClose = () => {
  if (isBurning.value) return // already closing
  stopTimer()
  isBurning.value = true
  // Allow animation to play briefly before clearing
  setTimeout(() => {
    emit('clear')
  }, 1200) 
}

watch(() => props.items, (newItems) => {
  if (newItems && newItems.length > 0) {
    startTimer()
  } else {
    stopTimer()
  }
}, { immediate: true })

onUnmounted(() => {
  stopTimer()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes burnEffect {
  0% {
    filter: blur(0px) brightness(1);
    opacity: 1;
    transform: scale(1) translateY(0);
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.15);
  }
  30% {
    box-shadow: 0 0 30px rgba(250, 204, 21, 0.8), inset 0 0 20px rgba(239, 68, 68, 0.5);
    border-color: #facc15;
  }
  70% {
    filter: blur(2px) brightness(1.5) contrast(1.2);
    opacity: 0.8;
    transform: scale(0.95) translateY(-5px);
    box-shadow: 0 0 40px rgba(239, 68, 68, 1), inset 0 0 40px rgba(239, 68, 68, 0.8);
    border-color: #ef4444;
  }
  100% {
    filter: blur(8px) brightness(0.5);
    opacity: 0;
    transform: scale(0.85) translateY(-15px);
    box-shadow: 0 0 50px rgba(0, 0, 0, 0);
  }
}

.is-burning {
  animation: burnEffect 3.5s ease-in forwards !important;
  pointer-events: none;
}
</style>
