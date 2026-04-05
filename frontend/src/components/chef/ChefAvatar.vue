<template>
  <div class="flex flex-col items-center justify-center p-6 space-y-4">
    <div 
      class="relative w-32 h-32 rounded-full flex items-center justify-center transition-all duration-500"
      :class="avatarStyles"
    >
      <!-- Base SVG Icon -->
      <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 transition-transform duration-300 transform hover:scale-110" :class="iconStyles" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17a2 2 0 002 2h4a2 2 0 002-2v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.87-3.13-7-7-7z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 21h6" />
      </svg>
    </div>
    
    <div class="text-center">
      <h3 class="text-xl font-bold tracking-wider text-slate-100">THE CHEF</h3>
      <p class="text-xs uppercase tracking-[0.2em]" :class="textStyles">{{ emotionDisplay }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { chefState } from '../../composables/useChefFSM'

const emotionDisplay = computed(() => chefState.emotionDisplay)

// Dynamic Neo-Ukrainian / Danger styles based on emotion
const avatarStyles = computed(() => {
  const e = emotionDisplay.value.toUpperCase()
  if (['ANGRY', 'CHAOTIC', 'FURIOUS'].includes(e)) {
    return 'bg-red-900/30 border-4 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.5)]'
  }
  if (['PLAYFUL', 'CREATIVE'].includes(e)) {
    return 'bg-yellow-900/30 border-4 border-neoYellow shadow-[0_0_30px_rgba(250,204,21,0.3)]'
  }
  // Default/Serious/Idle
  return 'bg-slate-800 border-4 border-neoBlue shadow-[0_0_20px_rgba(59,130,246,0.3)]'
})

const iconStyles = computed(() => {
  const e = emotionDisplay.value.toUpperCase()
  if (['ANGRY', 'CHAOTIC', 'FURIOUS'].includes(e)) return 'text-red-400'
  if (['PLAYFUL', 'CREATIVE'].includes(e)) return 'text-neoYellow'
  return 'text-neoBlue'
})

const textStyles = computed(() => {
  const e = emotionDisplay.value.toUpperCase()
  if (['ANGRY', 'CHAOTIC'].includes(e)) return 'text-red-400 font-bold'
  return 'text-slate-400'
})
</script>
