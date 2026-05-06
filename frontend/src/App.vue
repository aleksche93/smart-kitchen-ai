<template>
  <div class="h-screen w-screen bg-transparent text-slate-200 overflow-y-auto font-sans relative">
    
    <!-- Background overlay to tone down the svg pattern -->
    <div class="absolute inset-0 bg-slate-900/90 -z-10 pointer-events-none"></div>

    <!-- Main App Container -->
    <div class="w-full h-full flex flex-col p-4 md:p-8 space-y-6">
      
      <!-- Top Title Bar -->
      <header class="flex justify-between items-center text-slate-400">
        <div class="flex items-center gap-6">
           <h1 class="text-2xl font-bold tracking-widest text-slate-100 flex items-center">
             <span class="text-neoBlue mr-1">Kozak</span><span class="text-neoYellow">EYE</span><span class="text-yellow-300 text-sm -mt-1">OS</span>
           </h1>
           <!-- Identity Dropdown Header Module -->
           <div class="relative z-50">
              <div @click="isMenuOpen = !isMenuOpen" class="flex items-center gap-3 cursor-pointer p-1.5 pr-3 rounded-full bg-slate-800/50 border border-slate-700 hover:border-neoBlue transition-all">
                 <!-- Avatar Small -->
                 <ChefAvatar :mood="chefState.emotionDisplay" />
                 <div class="flex flex-col select-none">
                   <span class="text-xs font-bold text-slate-200 uppercase">The Chef</span>
                   <span class="text-[10px] uppercase font-bold" :class="emotionTextStyles">{{ chefState.emotionDisplay }}</span>
                 </div>
                 <svg :class="{'rotate-180 text-neoBlue': isMenuOpen}" class="w-4 h-4 ml-1 text-slate-500 transition-all duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
              </div>
              
              <!-- Dropdown Context -->
              <div :class="isMenuOpen ? 'opacity-100 visible translate-y-0' : 'opacity-0 invisible -translate-y-2'" class="absolute top-full left-0 mt-2 w-48 bg-slate-800 border border-slate-600 rounded-lg shadow-xl transition-all duration-300 overflow-hidden">
                 <button @click="handleReset" class="w-full text-left px-4 py-3 text-xs font-bold text-red-400 hover:bg-slate-700 block transition-colors border-b border-slate-700/50">Reset Session</button>
                 <button class="w-full text-left px-4 py-3 text-xs font-bold text-slate-400 hover:bg-slate-700 block disabled:opacity-50 transition-colors" disabled>Profile Settings</button>
              </div>
           </div>
        </div>
        
        <!-- Phase 12.2: The Dock (Top Header) -->
        <div class="flex items-center gap-3">
          <template v-for="w in minimizedWidgets" :key="w.widget_id">
             <button @click="restoreWidget(w)"
                     class="p-2 px-3 bg-slate-800/50 hover:bg-slate-700/80 rounded-xl border border-slate-600/50 transition-all shadow-lg hover:shadow-neoBlue/20 hover:border-neoBlue/50 group flex items-center gap-2"
                     :title="`Restore ${getWidgetTitle(w.widget_id)}`">
               <svg class="w-4 h-4 text-neoBlue group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" /></svg>
               <span class="text-xs uppercase font-bold text-slate-300 group-hover:text-neoBlue">{{ getWidgetTitle(w.widget_id) }}</span>
             </button>
          </template>
        </div>
        
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

        <div class="text-[10px] tracking-widest uppercase font-bold transition-all duration-300" 
             :class="serverStatus === 'Online' ? 'text-green-500' : 'text-red-500 animate-pulse'">
          Status: {{ serverStatus }}
        </div>
      </header>


      <!-- Phase 12.2: Spatial OS Workspace (Absolute Positioning) -->
      <main v-if="activeTab === 'kitchen'" class="flex-1 min-h-0 relative w-full h-full overflow-hidden">
        <template v-if="layoutStore.isLoaded">
           <WidgetWrapper 
              v-for="element in layoutStore.widgets"
              :key="element.widget_id"
              :widget="element" 
              :title="getWidgetTitle(element.widget_id)"
              :isFocused="activeWidget === element.widget_id"
              :showClose="element.widget_id === 'thought_ticker'"
              @focus="activeWidget = element.widget_id"
              @close="() => { element.is_collapsed = true; layoutStore.saveLayout() }"
              @update:collapse="(val) => { element.is_collapsed = val; layoutStore.saveLayout() }"
           >
              <div class="h-full flex flex-col">
                <FridgeList v-if="element.widget_id === 'fridge'" />
                
                <div v-else-if="element.widget_id === 'chef_hub'" class="flex flex-col relative h-full pr-2">
                   <InteractionZone @artifact="onArtifact" />
                </div>
                
                <AdviceDisplay
                  v-else-if="element.widget_id === 'advice'"
                  class="pr-2"
                />
              </div>
           </WidgetWrapper>
        </template>
        
        <div v-else class="h-full flex items-center justify-center text-slate-500 animate-pulse">
           Loading Workspace...
        </div>
      </main>

      <!-- Full Layout for Receipt Archive -->
      <main v-else-if="activeTab === 'archive'" class="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
        <ReceiptArchive />
      </main>

    </div>

    <!-- Floating ThoughtTicker (Global, outside grid) -->
    <ThoughtTicker />

    <!-- Phase 12.1 Step C: Focus Mode Overlay (Teleport) -->
    <Teleport to="body">
      <Transition name="focus-overlay">
        <div v-if="layoutStore.focusedArtifact"
             class="fixed inset-0 z-[9999] flex items-center justify-center">
          <!-- Backdrop blur -->
          <div class="absolute inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity duration-300"
               @click="layoutStore.clearFocusedArtifact()"></div>
          <!-- Focused Artifact Card -->
          <div class="relative z-10 w-full max-w-2xl max-h-[80vh] mx-4 overflow-y-auto custom-scrollbar">
            <ArtifactCard
              :artifact="layoutStore.focusedArtifact"
              :isFocused="true"
              :rotationAngle="0"
              :zIndex="100"
              @close="layoutStore.clearFocusedArtifact()"
              @focus="() => {}"
            />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>

import { computed, ref, onMounted } from 'vue'
import { useKitchenAPI } from './composables/useKitchenAPI'
import { useLayoutStore } from './stores/layoutStore'
import WidgetWrapper from './components/ui/WidgetWrapper.vue'

import ChefAvatar from './components/chef/ChefAvatar.vue'
import FridgeList from './components/inventory/FridgeList.vue'
import InteractionZone from './components/chef/InteractionZone.vue'
import AdviceDisplay from './components/output/AdviceDisplay.vue'
import ArtifactCard from './components/output/ArtifactCard.vue'
import ReceiptArchive from './views/ReceiptArchive.vue'
import ThoughtTicker from './components/chef/ThoughtTicker.vue'
import { useChefFSM, chefState } from './composables/useChefFSM'

const { activeTab } = useKitchenAPI()
const { resetState } = useChefFSM()

const isMenuOpen = ref(false)

const onArtifact = (artifactData) => {
  layoutStore.addArtifact(artifactData)
}

const handleReset = () => {
    resetState()
    isMenuOpen.value = false
}

const emotionIconStyles = computed(() => {
  const e = chefState.emotionDisplay.toUpperCase()
  if (['ANGRY', 'CHAOTIC', 'FURIOUS'].includes(e)) return 'text-red-400 border-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'
  if (['PLAYFUL', 'CREATIVE'].includes(e)) return 'text-neoYellow border-neoYellow shadow-[0_0_10px_rgba(250,204,21,0.3)]'
  return 'text-neoBlue'
})

const emotionTextStyles = computed(() => {
  const e = chefState.emotionDisplay.toUpperCase()
  if (['ANGRY', 'CHAOTIC'].includes(e)) return 'text-red-400'
  return 'text-neoBlue opacity-80'
})

const layoutStore = useLayoutStore()
const activeWidget = ref(null)

const minimizedWidgets = computed(() => {
  return layoutStore.widgets.filter(w => w.isMinimized)
})

const restoreWidget = (widget) => {
  if (activeTab.value !== 'kitchen') {
    activeTab.value = 'kitchen'
  }
  widget.isMinimized = false
  layoutStore.bringToFront(widget.widget_id)
  layoutStore.saveLayout()
}

const serverStatus = ref('Checking...')
let pingInterval = null

const checkHealth = () => {
  fetch('http://localhost:8000/api/v1/health')
    .then(res => {
      serverStatus.value = res.ok ? 'Online' : 'Offline'
    })
    .catch(() => {
      serverStatus.value = 'Offline'
    })
}

onMounted(() => {
  layoutStore.fetchLayout()
  checkHealth()
  pingInterval = setInterval(checkHealth, 5000)
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (pingInterval) clearInterval(pingInterval)
})

const getWidgetTitle = (widgetId) => {
  if (widgetId === 'fridge') return 'Inventory'
  if (widgetId === 'chef_hub') return 'Command Hub'
  if (widgetId === 'advice') return "Chef's Advice"
  return 'Widget'
}

const getMinHeight = (widgetId) => {
  if (widgetId === 'chef_hub' || widgetId === 'advice') return 450
  return 0
}

const getMaxHeight = (widgetId) => {
  if (widgetId === 'fridge') return 500
  if (widgetId === 'advice') return layoutStore.isAdviceMaximized ? 800 : 300
  return 500
}

// Phase 12.1 Step C: Dynamic Grid Column Span
const getWidgetColSpan = (widgetId) => {
  if (widgetId === 'advice' && layoutStore.isAdviceMaximized) {
    return 'col-span-1 md:col-span-2'
  }
  return 'col-span-1'
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

/* Focus Overlay transitions */
.focus-overlay-enter-active {
  transition: opacity 0.3s ease;
}
.focus-overlay-leave-active {
  transition: opacity 0.2s ease;
}
.focus-overlay-enter-from,
.focus-overlay-leave-to {
  opacity: 0;
}
</style>
