<template>
  <div class="space-y-3">
    <h4 class="text-lg font-bold text-emerald-400">{{ list.title || 'Список покупок' }}</h4>
    
    <div v-for="(category, catIdx) in categories" :key="catIdx" class="space-y-1.5">
      <h5 class="text-xs uppercase tracking-widest text-slate-400 font-bold flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        {{ category.name || 'Інше' }}
      </h5>
      <div v-for="(item, i) in category.items" :key="i"
           class="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/30 group cursor-pointer hover:border-emerald-500/30 transition-all"
           @click="item._checked = !item._checked">
        <!-- Checkbox -->
        <div class="w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-all"
             :class="item._checked ? 'bg-emerald-500 border-emerald-500' : 'border-slate-600'">
          <svg v-if="item._checked" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <span class="text-sm flex-1" :class="item._checked ? 'text-slate-500 line-through' : 'text-slate-300'">
          {{ item.name || item }}
        </span>
        <span v-if="item.quantity" class="text-[10px] text-slate-500">{{ item.quantity }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'

const props = defineProps({
  data: { type: Object, required: true }
})

const list = computed(() => props.data || {})

const categories = computed(() => {
  const raw = list.value.categories || list.value.items || []
  if (Array.isArray(raw) && raw.length > 0 && typeof raw[0] === 'string') {
    return [{ name: 'Загальне', items: raw.map(r => reactive({ name: r, _checked: false })) }]
  }
  return raw.map(cat => ({
    name: cat.name || cat.category || 'Інше',
    items: (cat.items || []).map(item => reactive(typeof item === 'string' ? { name: item, _checked: false } : { ...item, _checked: false }))
  }))
})
</script>
