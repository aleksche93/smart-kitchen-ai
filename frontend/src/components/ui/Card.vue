<template>
  <div class="bg-neoGray/80 backdrop-blur-md rounded-xl border border-slate-700/50 shadow-2xl overflow-hidden flex flex-col">
    <!-- Header -->
    <div v-if="title" class="bg-slate-800/80 px-4 py-3 border-b border-slate-700/50 flex justify-between items-center">
      <h2 class="text-sm uppercase tracking-widest font-semibold text-slate-300">{{ title }}</h2>
      <slot name="header-actions"></slot>
    </div>
    <!-- Content -->
    <div class="p-4 flex-1 overflow-y-auto">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  }
})
</script>
