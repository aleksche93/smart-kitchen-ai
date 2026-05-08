<template>
  <div class="markdown-artifact space-y-4">
    <div 
      class="prose prose-invert prose-sm max-w-none text-slate-300 markdown-body leading-relaxed"
      v-html="formattedMarkdown"
    ></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true }
})

const formattedMarkdown = computed(() => {
  const text = props.data.content || props.data.text || ''
  if (!text) return ''

  // Simplistic markdown parser (same as in AdviceDisplay)
  const safeText = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");

  return safeText
    .replace(/^### (.*$)/gim, '<h3 class="text-keWheat font-bold mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-keYellow font-bold mt-6 mb-3 border-b border-slate-700/50 pb-1">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-black text-keYellow mb-4">$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-100 font-bold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-slate-400">$1</em>')
    .replace(/^\* (.*$)/gim, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^\- (.*$)/gim, '<li class="ml-4 list-disc">$1</li>')
    .replace(/\n/g, '<br/>')
})
</script>

<style scoped>
.markdown-artifact :deep(h2) {
  margin-top: 1.5rem;
  color: var(--ke-yellow, #fbbf24);
}
.markdown-artifact :deep(li) {
  margin-bottom: 0.25rem;
}
</style>
