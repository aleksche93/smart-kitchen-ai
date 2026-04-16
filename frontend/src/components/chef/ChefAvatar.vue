<template>
  <div 
    class="w-10 h-10 rounded-full flex items-center justify-center transition-all bg-slate-800 border-2 shadow-sm breathing-pulse"
    :class="avatarStyles"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 transition-colors duration-300" :class="iconStyles" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.2" d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17a2 2 0 002 2h4a2 2 0 002-2v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7z" /><path stroke-linecap="round" stroke-linejoin="round" d="M9 21h6" /></svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  mood: {
    type: String,
    default: 'IDLE'
  }
})

// Dynamic Neo-Ukrainian / Danger styles based on emotion prop
const avatarStyles = computed(() => {
  const e = (props.mood || '').toUpperCase()
  if (['ANGRY', 'CHAOTIC', 'FURIOUS'].includes(e)) {
    return 'border-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)] bg-red-900/20'
  }
  if (['PLAYFUL', 'CREATIVE'].includes(e)) {
    return 'border-neoYellow shadow-[0_0_10px_rgba(250,204,21,0.3)] bg-yellow-900/20'
  }
  // Default/Serious/Idle
  return 'border-neoBlue shadow-[0_0_10px_rgba(59,130,246,0.3)]'
})

const iconStyles = computed(() => {
  const e = (props.mood || '').toUpperCase()
  if (['ANGRY', 'CHAOTIC', 'FURIOUS'].includes(e)) return 'text-red-400'
  if (['PLAYFUL', 'CREATIVE'].includes(e)) return 'text-neoYellow'
  return 'text-neoBlue'
})
</script>

<style scoped>
/* Subtle heartbeat/breathing effect for vital kinetic presence */
@keyframes breathing {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 0px rgba(59, 130, 246, 0));
  }
  50% {
    transform: scale(1.08);
    filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.4));
  }
}

.breathing-pulse {
  animation: breathing 4s ease-in-out infinite;
}
</style>
