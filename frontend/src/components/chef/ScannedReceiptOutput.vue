<template>
  <div v-if="items && items.length > 0" class="mt-4 bg-slate-800/80 backdrop-blur-sm border border-slate-600 rounded-lg overflow-hidden shadow-xl">
    <div class="bg-neoBlue/20 border-b border-neoBlue/30 px-4 py-3 flex justify-between items-center">
      <h3 class="text-sm font-bold text-neoBlue uppercase tracking-wider flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Parsed Receipt Data
      </h3>
      <button @click="$emit('clear')" class="text-slate-400 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
    </div>
    <div class="max-h-48 overflow-y-auto custom-scrollbar">
      <table class="w-full text-left text-sm text-slate-300">
        <thead class="bg-slate-700/50 text-slate-400 sticky top-0 backdrop-blur-md">
          <tr>
            <th class="px-4 py-2 font-medium">Product Name</th>
            <th class="px-4 py-2 font-medium">Category</th>
            <th class="px-4 py-2 font-medium">Qty</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-700/50">
          <tr v-for="(item, idx) in items" :key="idx" class="hover:bg-slate-700/30 transition-colors">
            <td class="px-4 py-3 font-semibold text-slate-200 capitalize">{{ item.name }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 rounded-md bg-slate-700/80 text-[10px] uppercase font-bold tracking-wider text-slate-300 border border-slate-600">
                {{ item.category || 'Other' }}
              </span>
            </td>
            <td class="px-4 py-3 flex items-center space-x-1">
              <span class="text-neoYellow font-mono">{{ item.quantity || item.amount || 1 }}</span>
              <span class="text-slate-500 text-xs">{{ item.unit || 'pcs' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
defineEmits(['clear'])
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}
</style>
