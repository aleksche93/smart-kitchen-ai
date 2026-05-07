<template>
  <div class="space-y-3">
    <div class="flex items-center gap-2">
      <span class="text-2xl animate-pulse">⚠️</span>
      <h4 class="text-lg font-bold text-red-400">{{ alert.title || 'Waste Alert' }}</h4>
    </div>

    <p v-if="alert.description" class="text-sm text-slate-300 leading-relaxed">{{ alert.description }}</p>

    <!-- Expiring Items -->
    <div v-if="expiringItems.length" class="space-y-1.5">
      <h5 class="text-xs uppercase tracking-widest text-red-400/80 font-bold">Продукти під загрозою</h5>
      <div v-for="(item, i) in expiringItems" :key="i"
           class="flex items-center justify-between px-3 py-2 rounded-lg bg-red-950/30 border border-red-900/40">
        <div class="flex items-center gap-2">
          <span class="text-sm">🔴</span>
          <span class="text-sm text-red-200">{{ item.name || item }}</span>
        </div>
        <span v-if="item.expires_in" class="text-[10px] uppercase tracking-wider font-bold text-red-400 bg-red-950/50 px-2 py-0.5 rounded-full">
          {{ item.expires_in }}
        </span>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="recommendations.length" class="space-y-1.5 pt-2 border-t border-slate-700/30">
      <h5 class="text-xs uppercase tracking-widest text-slate-400 font-bold">Рекомендації</h5>
      <ul class="space-y-1 text-sm text-slate-300">
        <li v-for="(rec, i) in recommendations" :key="i" class="flex items-start gap-2">
          <span class="text-keYellow shrink-0">💡</span>
          <span>{{ rec }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true }
})

const alert = computed(() => props.data || {})
const expiringItems = computed(() => {
  const raw = alert.value.items || alert.value.expiring_items || []
  return Array.isArray(raw) ? raw : []
})
const recommendations = computed(() => {
  const raw = alert.value.recommendations || alert.value.suggestions || []
  return Array.isArray(raw) ? raw : []
})
</script>
