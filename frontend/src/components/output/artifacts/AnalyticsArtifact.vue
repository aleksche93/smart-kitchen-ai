<template>
  <div class="analytics-artifact space-y-3">

    <!-- Chef's Summary: Compact & Italic -->
    <div class="px-3 py-2 bg-slate-800/60 rounded-xl border border-cyan-500/20 shadow-inner">
      <p class="text-[12px] text-slate-300 italic leading-snug">{{ data.summary }}</p>
    </div>

    <!-- Mini Stats Grid -->
    <div class="grid grid-cols-3 gap-2">
      <div class="flex flex-col items-center justify-center p-1.5 bg-slate-800/40 rounded-lg border border-slate-700/40">
        <span class="text-sm font-black text-slate-200">{{ data.total_items }}</span>
        <span class="text-[8px] uppercase tracking-tighter text-slate-500">{{ $t('artifact.analytics.total') }}</span>
      </div>
      <div class="flex flex-col items-center justify-center p-1.5 rounded-lg border"
           :class="data.waste_risk_count > 0 ? 'bg-red-900/20 border-red-700/40' : 'bg-slate-800/40 border-slate-700/40'">
        <span class="text-sm font-black" :class="data.waste_risk_count > 0 ? 'text-red-400' : 'text-slate-200'">
          {{ data.waste_risk_count }}
        </span>
        <span class="text-[8px] uppercase tracking-tighter text-slate-500">{{ $t('artifact.analytics.at_risk') }}</span>
      </div>
      <div class="flex flex-col items-center justify-center p-1.5 bg-emerald-900/10 rounded-lg border border-emerald-700/30">
        <span class="text-sm font-black text-emerald-400">{{ data.fresh_items?.length || 0 }}</span>
        <span class="text-[8px] uppercase tracking-tighter text-slate-500">{{ $t('artifact.analytics.fresh') }}</span>
      </div>
    </div>

    <!-- Items Grid: Critical & Warning -->
    <div v-if="data.critical_items?.length || data.warning_items?.length" class="space-y-2">
      <!-- Critical Chips -->
      <div v-if="data.critical_items?.length" class="flex flex-wrap gap-1.5">
        <div v-for="(item, i) in data.critical_items" :key="`crit-${i}`"
             class="flex items-center gap-1.5 px-2 py-1 rounded-md bg-red-900/30 border border-red-500/20 text-[11px] text-red-200">
          <span class="font-bold truncate max-w-[80px]">{{ item.name }}</span>
          <span class="text-[9px] opacity-60">{{ item.amount }}{{ item.unit }}</span>
          <span class="px-1 py-0.5 rounded bg-red-800/60 text-[8px] font-black tracking-tighter">!{{ item.days_left }}d</span>
        </div>
      </div>

      <!-- Warning Chips -->
      <div v-if="data.warning_items?.length" class="flex flex-wrap gap-1.5">
        <div v-for="(item, i) in data.warning_items" :key="`warn-${i}`"
             class="flex items-center gap-1.5 px-2 py-1 rounded-md bg-amber-900/20 border border-amber-500/20 text-[11px] text-amber-100">
          <span class="font-bold truncate max-w-[80px]">{{ item.name }}</span>
          <span class="text-[9px] opacity-60">{{ item.amount }}{{ item.unit }}</span>
          <span class="text-[9px] font-bold text-amber-400/80">{{ item.days_left }}d</span>
        </div>
      </div>
    </div>

    <!-- Fresh Items (Micro-list in details) -->
    <details v-if="data.fresh_items?.length"
             class="group bg-slate-800/20 rounded-lg border border-slate-700/20 overflow-hidden">
      <summary class="flex items-center justify-between px-3 py-1.5 cursor-pointer
                      list-none [&::-webkit-details-marker]:hidden hover:bg-slate-700/20 transition-colors">
        <span class="text-[9px] uppercase tracking-widest font-black text-slate-500 group-open:text-emerald-500/70">
          🌿 {{ $t('artifact.analytics.fresh') }} ({{ data.fresh_items.length }})
        </span>
        <svg class="w-2.5 h-2.5 text-slate-600 group-open:rotate-180 transition-transform"
             fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </summary>
      <div class="px-2 pb-2 grid grid-cols-2 gap-1 pt-1">
        <div v-for="(item, i) in data.fresh_items" :key="`fresh-${i}`"
             class="px-2 py-1 rounded border border-slate-700/10 bg-slate-800/10 text-[10px] text-slate-400 flex justify-between">
          <span class="truncate max-w-[60px]">{{ item.name }}</span>
          <span class="opacity-40">{{ item.days_left }}d</span>
        </div>
      </div>
    </details>

    <div v-if="!data.total_items" class="text-center py-4 text-slate-600">
      <p class="text-[10px] italic">{{ $t('artifact.analytics.empty') }}</p>
    </div>

  </div>
</template>

<script setup>
/**
 * Phase 13.5: Compact Analytics UI.
 * Uses a chip-based grid layout for maximum data density.
 * Strictly SFC Script Setup.
 */
const props = defineProps({
  data: { type: Object, required: true }
})
</script>

<style scoped>
.analytics-artifact {
  font-family: inherit;
}
details summary::-webkit-details-marker {
  display: none;
}
</style>
