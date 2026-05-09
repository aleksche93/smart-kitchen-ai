<template>
  <Teleport to="body">
    <Transition name="fade">
      <div 
        v-if="show" 
        class="fixed inset-0 z-[999] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center" 
        @click.self="close"
      >
        <div class="relative z-[1000] w-full max-w-full flex justify-center pointer-events-none">
           <!-- Ensure children can receive pointer events -->
           <div class="pointer-events-auto max-w-full">
             <slot></slot>
           </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
