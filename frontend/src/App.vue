<template>
  <div class="h-screen w-screen bg-slate-900 text-slate-200 overflow-auto font-sans relative">
    
    <!-- Background overlay to tone down the svg pattern -->
    <div class="fixed inset-0 bg-slate-900/90 -z-10 pointer-events-none"></div>

    <!-- Main App Container -->
    <div class="min-w-[1440px] min-h-[800px] h-full flex flex-col p-4 md:p-8 space-y-6">
      
      <!-- Top Title Bar -->
      <header class="flex justify-between items-center text-slate-400">
        <div class="flex items-center gap-6">
           <h1 class="text-2xl font-extrabold tracking-widest flex items-center drop-shadow-lg group">
             <span class="bg-gradient-to-r from-keBlue to-blue-400 bg-clip-text text-transparent">Kozak</span>
             <span class="relative flex items-center ml-1">
               <span class="bg-gradient-to-r from-keYellow to-yellow-200 bg-clip-text text-transparent">Eye</span>
               <!-- Kinetic Eye Indicator (Iris Style) -->
               <div class="ml-2 relative flex items-center justify-center w-4 h-4">
                 <span class="absolute w-full h-full bg-keYellow/20 rounded-full animate-pulse"></span>
                 <span class="absolute w-2 h-2 bg-keYellow rounded-full shadow-[0_0_10px_rgba(251,191,36,0.8)]"></span>
                 <span class="absolute w-4 h-4 border border-keYellow/30 rounded-full animate-[spin_4s_linear_infinite]"></span>
               </div>
             </span>
           </h1>
           <!-- Identity Dropdown Header Module -->
         <div class="relative z-[2000]">
              <div @click="isMenuOpen = !isMenuOpen" class="flex items-center gap-3 cursor-pointer p-1.5 pr-3 rounded-full bg-slate-800/50 border border-slate-700 hover:border-keBlue transition-all">
                 <!-- Avatar Small: Syncs with persistent chefStatus or momentary emotion -->
                 <ChefAvatar :mood="layoutStore.chefStatus !== 'IDLE' ? layoutStore.chefStatus : chefState.emotionDisplay" />
                 <div class="flex flex-col select-none">
                   <span class="text-xs font-bold text-slate-200 uppercase">{{ $t('ui.identity.title') }}</span>
                   <span class="text-[10px] uppercase font-bold" :class="emotionTextStyles">
                     {{ layoutStore.chefStatus !== 'IDLE' ? layoutStore.chefStatus : chefState.emotionDisplay }}
                   </span>
                 </div>
                 <svg :class="{'rotate-180 text-keBlue': isMenuOpen}" class="w-4 h-4 ml-1 text-slate-500 transition-all duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
              </div>
              
              <!-- Dropdown Context -->
              <div :class="isMenuOpen ? 'opacity-100 visible translate-y-0' : 'opacity-0 invisible -translate-y-2'" class="absolute z-[1050] top-full left-0 mt-2 w-48 bg-slate-800 border border-slate-600 rounded-lg shadow-xl transition-all duration-300 overflow-hidden">                 <button @click="handleReset" class="w-full text-left px-4 py-3 text-xs font-bold text-red-400 hover:bg-slate-700 block transition-colors border-b border-slate-700/50">{{ $t('ui.actions.reset_session') }}</button>
                 <button @click="() => { layoutStore.clearAllArtifacts(); isMenuOpen = false }" class="w-full text-left px-4 py-3 text-xs font-bold text-amber-400 hover:bg-slate-700 block transition-colors border-b border-slate-700/50">{{ $t('ui.actions.clear_artifacts') }}</button>
                 <button class="w-full text-left px-4 py-3 text-xs font-bold text-slate-400 hover:bg-slate-700 block disabled:opacity-50 transition-colors border-b border-slate-700/50" disabled>{{ $t('ui.actions.profile_settings') }}</button>
                 
                 <!-- Language Switcher -->
                 <div class="flex items-center justify-around p-2 bg-slate-900/50">
                   <button @click="i18nState.locale = 'en'" :class="i18nState.locale === 'en' ? 'text-keBlue' : 'text-slate-500'" class="text-[10px] font-bold uppercase hover:text-slate-300 transition-colors">English</button>
                   <div class="w-px h-3 bg-slate-700"></div>
                   <button @click="i18nState.locale = 'uk'" :class="i18nState.locale === 'uk' ? 'text-keBlue' : 'text-slate-500'" class="text-[10px] font-bold uppercase hover:text-slate-300 transition-colors">Українська</button>
                 </div>
              </div>
           </div>
        </div>
        
        <!-- Phase 12.2: The Dock (Top Header) -->
        <div class="flex items-center gap-2">
          <template v-for="w in minimizedWidgets" :key="w.widget_id">
             <button @click="restoreWidget(w)"
                     class="p-2 px-2 bg-slate-800/50 hover:bg-slate-700/80 rounded-xl border border-slate-600/50 transition-all shadow-lg hover:shadow-keBlue/20 hover:border-keBlue/50 group flex  items-center gap-1"
                     :title="`Restore ${getWidgetTitle(w.widget_id)}`">
               <svg class="w-4 h-4 text-keBlue group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" /></svg>
               <span class="text-xs uppercase font-bold text-slate-300 group-hover:text-keBlue">{{ getWidgetTitle(w.widget_id) }}</span>
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
                   :class="activeTab === 'kitchen' ? 'text-keBlue' : 'text-slate-400 hover:text-slate-200'" 
                   class="relative w-1/2 z-10 py-1.5 text-xs font-bold uppercase tracking-wider transition-colors rounded-full text-center">
             {{ $t('ui.tabs.kitchen') }}
           </button>
           <button @click="activeTab = 'archive'" 
                   :class="activeTab === 'archive' ? 'text-keBlue' : 'text-slate-400 hover:text-slate-200'" 
                   class="relative w-1/2 z-10 py-1.5 text-xs font-bold uppercase tracking-wider transition-colors rounded-full text-center">
             {{ $t('ui.tabs.archive') }}
           </button>
        </div>

        <div class="text-[10px] tracking-widest uppercase font-bold transition-all duration-300" 
             :class="serverStatus === 'Online' ? 'text-green-500' : 'text-red-500 animate-pulse'">
          {{ $t('ui.status.label') }}: {{ serverStatus }}
        </div>
      </header>


      <!-- Phase 12.2: Spatial OS Workspace (Absolute Positioning) -->
      <main v-if="activeTab === 'kitchen'" class="flex-1 min-h-0 relative w-full h-full overflow-hidden">
        <template v-if="layoutStore.isLoaded">
          <template v-for="element in layoutStore.widgets" :key="element.widget_id">
            <WidgetWrapper 
               v-if="element.widget_id !== 'thought_ticker'"
               :widget="element" 
               :title="getWidgetTitle(element.widget_id)"
               :isFocused="activeWidget === element.widget_id"
               :showClose="false"
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
            
            <ThoughtTicker v-else-if="element.widget_id === 'thought_ticker'" />
          </template>
        </template>
        
        <div v-else class="h-full flex items-center justify-center text-slate-500 animate-pulse">
           {{ $t('ui.status.loading') }}
        </div>
      </main>

      <!-- Full Layout for Receipt Archive -->
      <main v-else-if="activeTab === 'archive'" class="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
        <ReceiptArchive />
      </main>

    </div>

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
import { useI18n, i18nState } from './plugins/i18n'

const { t } = useI18n()
const { activeTab } = useKitchenAPI()
const { resetState, fetchChefState } = useChefFSM()

const isMenuOpen = ref(false)

const onArtifact = (artifactData) => {
  layoutStore.upsertArtifact(artifactData)
}

const handleReset = () => {
    resetState()
    isMenuOpen.value = false
}

const emotionIconStyles = computed(() => {
  const e = chefState.emotionDisplay.toUpperCase()
  if (['ANGRY', 'CHAOTIC', 'FURIOUS'].includes(e)) return 'text-red-400 border-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'
  if (['PLAYFUL', 'CREATIVE'].includes(e)) return 'text-keYellow border-keYellow shadow-[0_0_10px_rgba(250,204,21,0.3)]'
  return 'text-keBlue'
})

const emotionTextStyles = computed(() => {
  const e = chefState.emotionDisplay.toUpperCase()
  if (['ANGRY', 'CHAOTIC'].includes(e)) return 'text-red-400'
  return 'text-keBlue opacity-80'
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

const serverStatus = ref(t('ui.status.loading'))
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
  fetchChefState()
  checkHealth()
  pingInterval = setInterval(checkHealth, 5000)
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (pingInterval) clearInterval(pingInterval)
})

const getWidgetTitle = (widgetId) => {
  if (widgetId === 'fridge') return t('ui.widgets.inventory')
  if (widgetId === 'chef_hub') return t('ui.widgets.command_hub')
  if (widgetId === 'advice') return t('ui.widgets.chef_advice')
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
