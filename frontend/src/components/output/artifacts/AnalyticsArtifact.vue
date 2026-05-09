<template>
  <div class="analytics-artifact space-y-4">

    <!-- Chef's Summary -->
    <div class="px-4 py-3 bg-slate-800/60 rounded-xl border border-cyan-500/20 shadow-inner">
      <p class="text-sm text-slate-300 italic leading-relaxed">{{ data.summary }}</p>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-3 gap-2">
      <div class="flex flex-col items-center p-2 bg-slate-800/40 rounded-lg border border-slate-700/40">
        <span class="text-lg font-black text-slate-200">{{ data.total_items }}</span>
        <span class="text-[9px] uppercase tracking-widest text-slate-400">{{ $t('artifact.analytics.total') }}</span>
      </div>
      <div class="flex flex-col items-center p-2 rounded-lg border"
           :class="data.waste_risk_count > 0 ? 'bg-red-900/20 border-red-700/40' : 'bg-slate-800/40 border-slate-700/40'">
        <span class="text-lg font-black" :class="data.waste_risk_count > 0 ? 'text-red-400' : 'text-slate-200'">
          {{ data.waste_risk_count }}
        </span>
        <span class="text-[9px] uppercase tracking-widest text-slate-400">{{ $t('artifact.analytics.at_risk') }}</span>
      </div>
      <div class="flex flex-col items-center p-2 bg-emerald-900/20 rounded-lg border border-emerald-700/40">
        <span class="text-lg font-black text-emerald-400">{{ data.fresh_items?.length || 0 }}</span>
        <span class="text-[9px] uppercase tracking-widest text-slate-400">{{ $t('artifact.analytics.fresh') }}</span>
      </div>
    </div>

    <!-- CRITICAL tier -->
    <ItemTier
      v-if="data.critical_items?.length"
      :items="data.critical_items"
      :label="$t('artifact.analytics.critical')"
      priority="CRITICAL"
    />

    <!-- WARNING tier -->
    <ItemTier
      v-if="data.warning_items?.length"
      :items="data.warning_items"
      :label="$t('artifact.analytics.warning')"
      priority="WARNING"
    />

    <!-- FRESH tier (collapsible, closed by default) -->
    <details v-if="data.fresh_items?.length"
             class="group bg-slate-800/30 rounded-xl border border-slate-700/30 overflow-hidden">
      <summary class="flex items-center justify-between px-4 py-2.5 cursor-pointer list-none
                      [&::-webkit-details-marker]:hidden hover:bg-slate-700/20 transition-colors">
        <span class="text-[10px] uppercase tracking-widest font-black text-emerald-400/80">
          🌿 {{ $t('artifact.analytics.fresh') }} ({{ data.fresh_items.length }})
        </span>
        <svg class="w-3 h-3 text-slate-500 group-open:rotate-180 transition-transform duration-300"
             fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </summary>
      <div class="px-4 pb-3">
        <ItemTier :items="data.fresh_items" priority="FRESH" />
      </div>
    </details>

    <!-- Empty state -->
    <div v-if="!data.total_items" class="text-center py-6 text-slate-500">
      <span class="text-2xl">🛒</span>
      <p class="text-xs mt-2 italic">{{ $t('artifact.analytics.empty') }}</p>
    </div>

  </div>
</template>

<script setup>
import { useI18n } from '../../../plugins/i18n'

const { t } = useI18n()

const props = defineProps({
  data: { type: Object, required: true }
})

// Inline sub-component for tier rows (no file needed, DRY)
const ItemTier = {
  props: { items: Array, label: String, priority: String },
  template: `
    <div class="space-y-1">
      <div v-if="label" class="flex items-center gap-2 mb-2">
        <span class="text-[9px] uppercase tracking-widest font-black"
              :class="{
                'text-red-400': priority === 'CRITICAL',
                'text-amber-400': priority === 'WARNING',
                'text-emerald-400': priority === 'FRESH'
              }">
          {{ priority === 'CRITICAL' ? '🔴' : priority === 'WARNING' ? '🟡' : '🟢' }} {{ label }}
        </span>
        <div class="flex-1 h-px bg-current opacity-20"></div>
      </div>
      <div v-for="(item, i) in items" :key="i"
           class="flex items-center justify-between px-3 py-2 rounded-lg border text-sm"
           :class="{
             'bg-red-900/20 border-red-700/30 text-red-200': priority === 'CRITICAL',
             'bg-amber-900/20 border-amber-700/30 text-amber-200': priority === 'WARNING',
             'bg-slate-800/30 border-slate-700/20 text-slate-300': priority === 'FRESH'
           }">
        <span class="font-medium capitalize truncate">{{ item.name }}</span>
        <div class="flex items-center gap-2 shrink-0 ml-2">
          <span class="text-[10px] text-slate-400">{{ item.amount }}{{ item.unit }}</span>
          <span v-if="item.days_left !== null && item.days_left !== undefined"
                class="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
                :class="{
                  'bg-red-800/60 text-red-300': priority === 'CRITICAL',
                  'bg-amber-800/60 text-amber-300': priority === 'WARNING',
                  'bg-slate-700/60 text-slate-400': priority === 'FRESH'
                }">
            {{ item.days_left }}d
          </span>
        </div>
      </div>
    </div>
  `
}
</script>

<style scoped>
.analytics-artifact {
  font-family: inherit;
}
</style>
