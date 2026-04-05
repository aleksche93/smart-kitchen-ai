<template>
  <div class="relative w-full overflow-hidden bg-black/40 rounded-md border border-slate-700/50 p-2 font-mono text-xs">
    <div class="flex items-center justify-between">
      <span class="text-green-400 opacity-80 blink-cursor mr-2">_></span>
      <div class="flex-1 overflow-hidden relative h-4">
        <transition name="fade" mode="out-in">
          <span v-if="!zenMode" :key="currentThought" class="absolute w-full truncate text-slate-400">
            {{ currentThought }}
          </span>
          <span v-else class="absolute w-full text-slate-600 block text-center">
            [Zen Mode Engaged]
          </span>
        </transition>
      </div>
      <button 
        @click="zenMode = !zenMode" 
        class="ml-2 text-slate-500 hover:text-neoYellow transition-colors"
        title="Toggle Zen Mode"
      >
        🧘
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const zenMode = ref(false)
const thoughts = [
  "Reading Flavor Bible...",
  "Recalculating umami ratios...",
  "Watching gastro-YouTube shorts...",
  "Judging your chaotic history...",
  "Dreaming of 3 Michelin stars...",
  "Waiting for input..."
]

const currentThought = ref(thoughts[0])
let interval

onMounted(() => {
  interval = setInterval(() => {
    if (!zenMode.value) {
      const rd = Math.floor(Math.random() * thoughts.length)
      currentThought.value = thoughts[rd]
    }
  }, 5000)
})

onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.blink-cursor {
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
