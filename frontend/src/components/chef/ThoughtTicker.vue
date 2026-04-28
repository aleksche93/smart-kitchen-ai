<template>
  <Transition name="melt">
    <div v-show="isVisible" class="flex flex-col h-full w-full font-mono text-xs text-green-400 bg-transparent">
        

      <!-- Terminal Body -->
      <div class="p-3 flex-1 overflow-y-auto relative flex flex-col justify-end">
        <transition-group name="slide-up" tag="div" class="flex flex-col space-y-1">
          <div v-for="(log, idx) in thoughts" :key="log.id" class="flex items-start">
             <span class="opacity-70 mr-2">$</span>
             <span v-if="idx !== thoughts.length - 1" class="opacity-50">{{ log.text }}</span>
             <span v-else>{{ displayText }}</span>
             <span v-if="idx === thoughts.length - 1" class="blink-cursor ml-1">_</span>
          </div>
        </transition-group>
      </div>
    </div>
  </Transition>
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
let hideTimer = null

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

// Keep ticker visible if new thoughts arrive
watch(() => thoughts.value.length, async () => {
  isVisible.value = true
  if (hideTimer) clearTimeout(hideTimer)
  
  if (thoughts.value.length > 0) {
    const latestThought = thoughts.value[thoughts.value.length - 1]
    abort() // Stop any ongoing typing
    // Start typing the new thought
    await type(latestThought.text)
  }

  hideTimer = setTimeout(() => {
    if (!isLoading.value) isVisible.value = false
  }, 5000)
})

onMounted(() => {
  chefStore.startSarcasticEngine()
})

onUnmounted(() => {
  clearTimeout(hideTimer)
  chefStore.stopSarcasticEngine()
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
.melt-enter-active,
.melt-leave-active {
  transition: all 3000ms ease-out;
}
.melt-enter-from,
.melt-leave-to {
  opacity: 0;
  filter: blur(8px);
  transform: translateY(-10px);
}
</style>
