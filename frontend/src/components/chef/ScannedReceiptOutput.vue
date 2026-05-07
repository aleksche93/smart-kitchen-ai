<template>
  <Teleport to="body">
    <div v-if="items && items.length > 0" class="fixed bottom-6 right-6 w-[400px] z-50 animate-fade-in-up">
      <div class="bg-slate-800/90 backdrop-blur-md border border-keBlue/30 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(56,189,248,0.15)] flex flex-col max-h-[60vh]">
        <div class="bg-keBlue/20 border-b border-keBlue/30 px-4 py-3 flex justify-between items-center shrink-0">
          <h3 class="text-sm font-bold text-keBlue uppercase tracking-wider flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Parsed Receipt Data
          </h3>
          <button @click="$emit('clear')" class="text-slate-400 hover:text-white transition-colors bg-slate-700/50 hover:bg-slate-600 rounded-full p-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="overflow-y-auto custom-scrollbar flex-1 p-2">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-700/50 text-slate-400 sticky top-0 backdrop-blur-md z-10 rounded-lg">
              <tr>
                <th class="px-3 py-2 font-medium rounded-tl-lg">Product</th>
                <th class="px-3 py-2 font-medium">Cat</th>
                <th class="px-3 py-2 font-medium rounded-tr-lg">Qty</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/50">
              <tr v-for="(item, idx) in items" :key="idx" class="hover:bg-slate-700/30 transition-colors">
                <td class="px-3 py-2 font-semibold text-slate-200 capitalize truncate max-w-[150px]">{{ item.name }}</td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 rounded-md bg-slate-700/80 text-[10px] uppercase font-bold tracking-wider text-slate-300 border border-slate-600">
                    {{ item.category || 'Other' }}
                  </span>
                </td>
                <td class="px-3 py-2 flex items-center space-x-1">
                  <span class="text-keYellow font-mono">{{ item.quantity || item.amount || 1 }}</span>
                  <span class="text-slate-500 text-[10px] uppercase">{{ item.unit || 'pcs' }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </Teleport>
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
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in-up {
  animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
