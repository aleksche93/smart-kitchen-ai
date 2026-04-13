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
        
        <!-- Sliding Pill Navigation -->
        <div class="relative flex p-1 bg-slate-900/50 backdrop-blur-md rounded-full border border-slate-700/50 w-64 shadow-inner">
           <!-- The Sliding Background -->
           <div class="absolute inset-y-1 bg-slate-700 shadow-md rounded-full transition-all duration-300 ease-out z-0"
                :class="activeTab === 'kitchen' ? 'left-1 w-[calc(50%-4px)]' : 'left-1/2 w-[calc(50%-4px)]'">
           </div>
           
           <button @click="activeTab = 'kitchen'" 
                   :class="activeTab === 'kitchen' ? 'text-neoBlue' : 'text-slate-400 hover:text-slate-200'" 
                   class="relative w-1/2 z-10 py-1.5 text-xs font-bold uppercase tracking-wider transition-colors rounded-full text-center">
             Kitchen
           </button>
           <button @click="activeTab = 'archive'" 
                   :class="activeTab === 'archive' ? 'text-neoBlue' : 'text-slate-400 hover:text-slate-200'" 
                   class="relative w-1/2 z-10 py-1.5 text-xs font-bold uppercase tracking-wider transition-colors rounded-full text-center">
             Archive
           </button>
        </div>

        <div class="text-xs tracking-widest uppercase opacity-60">Status: Online</div>
      </header>


      <!-- 3-Panel Layout Grid for Kitchen (Draggable) -->
      <main v-if="activeTab === 'kitchen'" class="flex-1 min-h-0">
        <draggable
          v-if="layoutStore.isLoaded"
          v-model="layoutStore.widgets"
          item-key="widget_id"
          class="grid grid-cols-1 md:grid-cols-12 gap-6 h-full"
          handle=".drag-handle"
          ghost-class="opacity-50"
          :animation="200"
        >
          <template #item="{ element }">
             <div :class="getColSpan(element.widget_id)" class="h-full flex flex-col justify-start">
                <WidgetWrapper 
                   :widget="element" 
                   :title="getWidgetTitle(element.widget_id)"
                   :isFocused="activeWidget === element.widget_id"
                   @focus="activeWidget = element.widget_id"
                   @update:collapse="(val) => { element.is_collapsed = val; layoutStore.saveLayout() }"
                >
                   <div class="h-full overflow-y-auto custom-scrollbar pr-2">
                     <FridgeList v-if="element.widget_id === 'fridge'" />
                     
                     <div v-else-if="element.widget_id === 'chef_hub'" class="flex flex-col relative h-full">
                        <ChefAvatar />
                        <InteractionZone />
                     </div>
                     
                     <AdviceDisplay v-else-if="element.widget_id === 'advice'" />
                   </div>
                </WidgetWrapper>
             </div>
          </template>
        </draggable>
        
        <div v-else class="h-full flex items-center justify-center text-slate-500 animate-pulse">
           Loading Workspace...
        </div>
      </main>

      <!-- Full Layout for Receipt Archive -->
      <main v-else-if="activeTab === 'archive'" class="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
        <ReceiptArchive />
      </main>

    </div>
  </div>
</template>

<script setup>

import { computed, ref, onMounted } from 'vue'
import { useKitchenAPI } from './composables/useKitchenAPI'
import { useLayoutStore } from './stores/layoutStore'
import draggable from 'vuedraggable'
import WidgetWrapper from './components/ui/WidgetWrapper.vue'

import FridgeList from './components/inventory/FridgeList.vue'
import ChefAvatar from './components/chef/ChefAvatar.vue'
import InteractionZone from './components/chef/InteractionZone.vue'
import AdviceDisplay from './components/output/AdviceDisplay.vue'
import ReceiptArchive from './views/ReceiptArchive.vue'

const { activeTab } = useKitchenAPI()

const layoutStore = useLayoutStore()
const activeWidget = ref(null)

onMounted(() => {
  layoutStore.fetchLayout()
})

const getColSpan = (widgetId) => {
  if (widgetId === 'fridge') return 'md:col-span-3'
  if (widgetId === 'chef_hub') return 'md:col-span-5'
  if (widgetId === 'advice') return 'md:col-span-4'
  return 'md:col-span-12'
}

const getWidgetTitle = (widgetId) => {
  if (widgetId === 'fridge') return 'Inventory'
  if (widgetId === 'chef_hub') return 'Command Hub'
  if (widgetId === 'advice') return 'Culinary Advice'
  return 'Widget'
}
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
