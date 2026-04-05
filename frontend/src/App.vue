<template>
  <div class="h-screen w-screen bg-transparent text-slate-200 overflow-hidden font-sans relative">
    
    <!-- Background overlay to tone down the svg pattern -->
    <div class="absolute inset-0 bg-slate-900/90 -z-10 pointer-events-none"></div>

    <!-- Main App Container -->
    <div class="container mx-auto h-full max-w-7xl flex flex-col p-4 md:p-8 space-y-6">
      
      <!-- Top Title Bar -->
      <header class="flex justify-between items-center text-slate-400">
        <h1 class="text-2xl font-bold tracking-widest text-slate-100 flex items-center">
          <span class="text-neoBlue mr-2">neo</span>KITCHEN<span class="text-neoYellow text-xs align-top ml-1">OS</span>
        </h1>
        <div class="text-xs tracking-widest uppercase opacity-60">Status: Online</div>
      </header>

      <!-- 3-Panel Layout Grid -->
      <main class="flex-1 grid grid-cols-1 md:grid-cols-12 gap-6 min-h-0">
        
        <!-- Left Panel: Inventory (Col span 3) -->
        <aside class="md:col-span-3 h-full overflow-y-auto pr-2 custom-scrollbar">
          <FridgeList />
        </aside>

        <!-- Center Panel: Stateful Chef (Col span 5) -->
        <section class="md:col-span-5 h-full flex flex-col justify-start md:justify-center overflow-y-auto pr-2 custom-scrollbar">
          <!-- Central Interactive Hub -->
          <div class="bg-neoGray/30 backdrop-blur-md rounded-2xl border border-slate-700/50 p-8 shadow-2xl relative my-auto">
             <ChefAvatar />
             <ThoughtTicker />
             <InteractionZone />
          </div>
        </section>

        <!-- Right Panel: Output & IoT Console (Col span 4) -->
        <aside class="md:col-span-4 h-full flex flex-col justify-between space-y-4 overflow-y-auto pr-2 custom-scrollbar">
           <AdviceDisplay />
           <!-- <ConsoleLog /> hidden for B2C Pivot -->
        </aside>

      </main>

    </div>
  </div>
</template>

<script setup>
import FridgeList from './components/inventory/FridgeList.vue'
import ChefAvatar from './components/chef/ChefAvatar.vue'
import ThoughtTicker from './components/chef/ThoughtTicker.vue'
import InteractionZone from './components/chef/InteractionZone.vue'
import AdviceDisplay from './components/output/AdviceDisplay.vue'
import ConsoleLog from './components/output/ConsoleLog.vue'
</script>

<style>
/* Global CSS is imported in index.css / style.css via main.js */
/* Danger mode styling attached to html body */
html.danger-zone body {
  @apply bg-red-950/40;
}
html.danger-zone .bg-slate-900\/90 {
  background-color: rgba(30, 0, 0, 0.9) !important;
}
</style>
