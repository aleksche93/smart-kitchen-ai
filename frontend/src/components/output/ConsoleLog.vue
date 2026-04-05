<template>
  <Card title="IoT Stub / Event Log" class="h-[35%] bg-black/60 border-neoDark shadow-inner">
    <div class="font-mono text-xs text-green-400/90 h-full overflow-y-auto space-y-2 p-1">
      <div v-if="chefState.toolCommands.length === 0" class="text-slate-600 italic">
        [No system events detected]
      </div>
      <div 
        v-for="(cmd, idx) in chefState.toolCommands" 
        :key="idx"
        class="border-l-2 border-neoBlue pl-2 py-1 bg-neoBlue/10 rounded-r-sm"
      >
        <span class="text-neoBlue font-bold block mb-1">> EXECUTE: {{ cmd.action }}</span>
        <span class="text-slate-400 break-words">{{ cmd.params }}</span>
      </div>
    </div>
  </Card>
</template>

<script setup>
import Card from '../ui/Card.vue'
import { chefState } from '../../composables/useChefFSM'
</script>
