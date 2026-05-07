<template>
  <div class="artifact-skeleton bg-slate-900/90 backdrop-blur-xl rounded-2xl border border-slate-700/30 overflow-hidden">
    <!-- Header Skeleton -->
    <div class="flex items-center gap-3 px-4 py-3 border-b border-slate-700/30">
      <div class="w-8 h-8 rounded-full bg-slate-800 shimmer"></div>
      <div class="flex-1 space-y-1.5">
        <div class="h-3 w-32 rounded-full bg-slate-800 shimmer"></div>
        <div class="h-2 w-20 rounded-full bg-slate-800 shimmer" style="animation-delay: 100ms"></div>
      </div>
    </div>

    <!-- Body Skeleton -->
    <div class="p-4 space-y-4">
      <!-- Title bar -->
      <div class="h-5 w-48 rounded-full bg-slate-800 shimmer" style="animation-delay: 200ms"></div>
      
      <!-- Ingredients grid -->
      <div class="grid grid-cols-2 gap-2">
        <div v-for="i in 4" :key="i"
             class="h-8 rounded-lg bg-slate-800 shimmer"
             :style="{ animationDelay: (200 + i * 80) + 'ms' }">
        </div>
      </div>

      <!-- Steps -->
      <div class="space-y-2">
        <div v-for="i in 3" :key="'s'+i"
             class="h-3 rounded-full bg-slate-800 shimmer"
             :style="{ width: (90 - i * 15) + '%', animationDelay: (500 + i * 100) + 'ms' }">
        </div>
      </div>
    </div>

    <!-- Pulsing indicator -->
    <div class="flex items-center justify-center gap-2 py-3 border-t border-slate-700/30">
      <span class="w-1.5 h-1.5 rounded-full bg-keBlue animate-ping"></span>
      <span class="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Chef is generating...</span>
    </div>
  </div>
</template>

<script setup>
// No props needed — pure presentational skeleton
</script>

<style scoped>
.shimmer {
  background: linear-gradient(
    90deg,
    rgba(30, 41, 59, 0.5) 25%,
    rgba(51, 65, 85, 0.8) 50%,
    rgba(30, 41, 59, 0.5) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
